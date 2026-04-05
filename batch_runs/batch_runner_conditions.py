# batch_runner_v3.py
import sys
import os
import time
import numpy as np
import concurrent.futures

# Pfad-Fix für den Ordner (falls über Terminal gestartet)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.parameters import Parameters
from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from simulation.logger import DataLogger

# --- 1. DIE FUNKTION FÜR EINEN EINZELNEN KERN ---
def run_single_simulation(args):
    """
    Diese Funktion läuft isoliert auf einem einzelnen CPU-Kern ab.
    Sie hat keinen Kontakt zu den anderen Kernen.
    """
    # Tuple entpacken (angepasst an die neuen Namen)
    (run_id, cond_name, angle, cond_g_mag, cond_actin_api, 
     cond_actin_bas, cond_actin_lat, initial_state, durchmesser, raumy, 
     cond_angle_dir, timestamp_main, dauer_pro_run) = args

    # Frisches Parameter-Objekt
    params = Parameters()
    params.raumy = raumy
    params.winkel_in_XY = angle

    # ---> KONTROLL-PARAMETER ÜBERSCHREIBEN <---
    params.g_mag = cond_g_mag
    params.ACTIN_FORCE_APICAL = cond_actin_api
    params.ACTIN_FORCE_BASAL = cond_actin_bas
    params.ACTIN_LATERAL_FORCE = cond_actin_lat
    # HINWEIS: LIMIT_X bleibt auf 50.0 für alle, da wir nur die Kraft auf 0 setzen!

    # WICHTIG: Echte Entropie für Multiprocessing zwingend erforderlich (wie im Original!)
    np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
    run_seed = np.random.randint(0, 10**9)
    np.random.seed(run_seed)
    params.current_seed = run_seed

    # Engine initialisieren (mit .copy() um das Original zu schützen)
    engine = SimulationEngine(initial_state.copy(), params)

    # Logger initialisieren - Pfad-Struktur exakt wie in deinem Original!
    filename = os.path.join(cond_angle_dir, f"run_{run_id:03d}_{timestamp_main}.csv")
    logger = DataLogger(filename, params, durchmesser, run_seed)

    sim_time = 0.0
    log_interval = 0.1
    next_log = 0.0

    run_start = time.time()

    # Simulations-Schleife (100 % identisch zu deinem Ansatz)
    while sim_time < dauer_pro_run:
        engine.step(params.dt)
        sim_time += params.dt
        
        if sim_time >= next_log:
            logger.log(sim_time, engine)
            next_log += log_interval

    run_duration = time.time() - run_start
    return f"  -> {cond_name} | {angle}° | Run {run_id:03d} (Seed: {run_seed}) gespeichert in {run_duration:.1f}s"


# --- 2. DIE MULTIPROCESSING VERWALTUNG ---
def run_batch_v3(anzahl_runs=100, dauer_pro_run=2000.0):
    # Gemeinsames Warmup
    params_base = Parameters()
    durchmesser = 25.0
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params_base.CELL_WALL
    params_base.raumy = raumy
    params_base.winkel_in_XY = 0
    
    print("--- Phase 1: Initialisiere/Lade gemeinsames Warmup (Basis) ---")
    initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))

    # Die Kontroll-Bedingungen definieren (mit den jeweils gewünschten Winkeln!)
    conditions = [
        {
            "name": "0g_microgravity", 
            "g_mag": 0.0, 
            "actin_api": params_base.ACTIN_FORCE_APICAL, 
            "actin_bas": params_base.ACTIN_FORCE_BASAL, 
            "actin_lat": params_base.ACTIN_LATERAL_FORCE,
            "angles": [0]
        },
        {
            "name": "no_actin", 
            "g_mag": params_base.g_mag, 
            "actin_api": 0.0,  # Apikales Aktin aus!
            "actin_bas": 0.0,  # Basales Aktin aus!
            "actin_lat": 0.0,  # Laterales Aktin aus!
            "angles": [0, 90, 180]
        }
    ]
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    monster_dir = f"data/monster_run_v3_{timestamp_main}"
    os.makedirs(monster_dir, exist_ok=True)
    
    # Aufgaben (Tasks) für die Kerne vorbereiten
    tasks = []
    
    print("Erstelle verschachtelte Ordnerstruktur...")
    for cond in conditions:
        cond_name = cond["name"]
        cond_dir = os.path.join(monster_dir, cond_name)
        
        for angle in cond["angles"]:
            # Unterordner erstellen (Minuszeichen sicher im Namen verpacken)
            angle_str = str(angle).replace('-', 'minus_')
            cond_angle_dir = os.path.join(cond_dir, f"angle_{angle_str}")
            os.makedirs(cond_angle_dir, exist_ok=True)
            
            # Für jeden Run eine "Aufgabe" schnüren
            for i in range(1, anzahl_runs + 1):
                tasks.append((
                    i, cond_name, angle, cond["g_mag"], 
                    cond["actin_api"], cond["actin_bas"], cond["actin_lat"], 
                    initial_state, durchmesser, raumy, 
                    cond_angle_dir, timestamp_main, dauer_pro_run
                ))

    total_start = time.time()
    total_tasks = len(tasks)
    
    print(f"\n{'='*60}")
    print(f" Verteile {total_tasks} Simulationen auf 8 CPU-Kerne deines M3 Pro")
    print(f" Zurücklehnen. Das Biest arbeitet...")
    print(f"{'='*60}\n")

    # Der eigentliche Multiprocessing-Start (Exakt wie im Original!)
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_single_simulation, task) for task in tasks]
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                completed += 1
                print(f"[{completed}/{total_tasks}] {result}", flush=True)
            except Exception as exc:
                print(f"FEHLER in einem Run: {exc}")

    total_duration = (time.time() - total_start) / 3600
    print(f"\n{'='*50}")
    print(f"=== KONTROLL RUN V3 BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten gespeichert in: {monster_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_batch_v3(anzahl_runs=100, dauer_pro_run=2000.0)