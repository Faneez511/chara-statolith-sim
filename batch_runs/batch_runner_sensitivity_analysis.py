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
    run_id, angle, cond_name, modifier, initial_state, durchmesser, raumy, angle_dir, timestamp_main, dauer_pro_run = args

    # Frisches Parameter-Objekt aufsetzen
    params = Parameters()
    params.raumy = raumy
    params.winkel_in_XY = angle

    # ==========================================
    # SENSITIVITÄTS-MODIFIKATION (Das Herzstück)
    # ==========================================
    params.ACTIN_FORCE_APICAL *= modifier
    params.ACTIN_FORCE_BASAL *= modifier
    params.ACTIN_LATERAL_FORCE *= modifier

    # WICHTIG: Echte Entropie für Multiprocessing
    np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
    run_seed = np.random.randint(0, 10**9)
    np.random.seed(run_seed)
    params.current_seed = run_seed

    # Engine initialisieren
    engine = SimulationEngine(initial_state.copy(), params)

    # Logger initialisieren
    filename = os.path.join(angle_dir, f"run_{run_id:03d}_{timestamp_main}.csv")
    logger = DataLogger(filename, params, durchmesser, run_seed)

    sim_time = 0.0
    log_interval = 0.1
    next_log = 0.0

    run_start = time.time()

    # Simulations-Schleife
    while sim_time < dauer_pro_run:
        engine.step(params.dt)
        sim_time += params.dt
        
        if sim_time >= next_log:
            logger.log(sim_time, engine)
            next_log += log_interval

    run_duration = time.time() - run_start
    return f"  -> {cond_name} | {angle}° | Run {run_id:03d} (Seed: {run_seed}) in {run_duration:.1f}s"


# --- 2. DIE MULTIPROCESSING VERWALTUNG ---
def run_batch(anzahl_runs=100, dauer_pro_run=2000.0):
    
    # 1. KONFIGURATION FÜR DEN SENSITIVITY RUN
    angles = [0, 15, 45, 75, 90, 180]
    conditions = {
        "standard_100_actin": 1.0
    }
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    monster_dir = f"data/sensitivity_run_{timestamp_main}"
    os.makedirs(monster_dir, exist_ok=True)
    
    durchmesser = 25.0
    
    print(f"\n{'='*60}")
    print(f" STARTE SENSITIVITÄTS-ANALYSE (+/- 10% Aktin)")
    print(f"{'='*60}\n")

    total_start = time.time()

    # =======================================================
    # DIE SEQUENZIELLE SCHLEIFE FÜR DEINEN MANUELLEN TRICK
    # =======================================================
    # Wir iterieren über beide Konditionen nacheinander
    for cond_name, modifier in conditions.items():
        print(f"\n{'*'*50}")
        print(f" BEGINNE KONDITION: {cond_name.upper()} (Aktin x {modifier})")
        print(f"{'*'*50}")
        
        params_base = Parameters()
        mittelpunkt = durchmesser / 2.0
        raumy = mittelpunkt - params_base.CELL_WALL
        params_base.raumy = raumy
        
        # AKTIN AUCH IM WARMUP ANPASSEN, DAMIT DER STARTPUNKT PERFEKT STIMMT
        params_base.ACTIN_FORCE_APICAL *= modifier
        params_base.ACTIN_FORCE_BASAL *= modifier
        params_base.ACTIN_LATERAL_FORCE *= modifier
        
        print(f"-> Prüfe / Berechne Warmup für {cond_name}...")
        initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))
        
        print(f"-> Phase 2: Bereite Aufgaben für {cond_name} vor ---")
        tasks = []
        cond_dir = os.path.join(monster_dir, cond_name)
        os.makedirs(cond_dir, exist_ok=True)

        for angle in angles:
            angle_str = str(angle).replace('-', 'minus_')
            angle_dir = os.path.join(cond_dir, f"angle_{angle_str}")
            os.makedirs(angle_dir, exist_ok=True)
            
            for i in range(1, anzahl_runs + 1):
                tasks.append((i, angle, cond_name, modifier, initial_state, durchmesser, raumy, angle_dir, timestamp_main, dauer_pro_run))

        total_tasks_cond = len(tasks)
        print(f"\n{'='*60}")
        print(f" Starte {total_tasks_cond} Runs für {cond_name} auf CPU-Kernen")
        print(f" [!!] WICHTIG: JETZT HAST DU 75 MINUTEN ZEIT, DIE WARMUP-DATEI UMZUBENENNEN! [!!]")
        print(f"{'='*60}\n")

        # MULTIPROCESSING: Jetzt IN der Schleife! 
        # Er blockiert hier, bis die Kondition komplett fertig gerechnet ist.
        with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_single_simulation, task) for task in tasks]
            
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    completed += 1
                    print(f"[{completed}/{total_tasks_cond}] {result}", flush=True)
                except Exception as exc:
                    print(f"FEHLER in einem Run: {exc}")

        print(f"\n-> KONDITION {cond_name.upper()} ABGESCHLOSSEN!")
        # Wenn er hier ankommt, ist z.B. +10% komplett fertig und er springt oben zum nächsten Element (-10%).

    # Wenn BEIDE Konditionen abgearbeitet sind:
    total_duration = (time.time() - total_start) / 3600
    print(f"\n{'='*50}")
    print(f"=== SENSITIVITY RUN BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten gespeichert in: {monster_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_batch(anzahl_runs=100, dauer_pro_run=2000.0)