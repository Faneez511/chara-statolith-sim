# batch_runner_angles.py
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
    # Parameter auspacken
    run_id, angle, initial_state, durchmesser, raumy, angle_dir, timestamp_main, dauer_pro_run = args

    # Frisches Parameter-Objekt für diesen spezifischen Run aufsetzen
    params = Parameters()
    params.raumy = raumy
    params.winkel_in_XY = angle

    # WICHTIG: Echte Entropie für Multiprocessing zwingend erforderlich, 
    # da sonst geklonte Prozesse denselben Seed nutzen könnten!
    np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
    run_seed = np.random.randint(0, 10**9)
    np.random.seed(run_seed)
    params.current_seed = run_seed

    # Engine initialisieren (mit .copy() um das Original zu schützen)
    engine = SimulationEngine(initial_state.copy(), params)

    # Logger initialisieren - Pfad-Struktur exakt wie in deinem Original!
    filename = os.path.join(angle_dir, f"run_{run_id:03d}_{timestamp_main}.csv")
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
    return f"  -> {angle}° | Run {run_id:03d} (Seed: {run_seed}) gespeichert in {run_duration:.1f}s"


# --- 2. DIE MULTIPROCESSING VERWALTUNG ---
def run_batch(anzahl_runs=100, dauer_pro_run=2000.0):
    # Gemeinsames Warmup
    params_base = Parameters()
    durchmesser = 25.0
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params_base.CELL_WALL
    params_base.raumy = raumy
    
    print("--- Phase 1: Initialisiere/Lade gemeinsames Warmup ---")
    initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))

    # Die perfekten Winkel + die extra Winkel für R2 > 0.99
    angles = [0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90, 180]
    
    print(f"--- Phase 2: Starte Monster-Run für {len(angles)} Winkel (MULTICORE) ---")
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    monster_dir = f"data/monster_run_{timestamp_main}"
    os.makedirs(monster_dir, exist_ok=True)
    
    # Aufgaben (Tasks) für die Kerne vorbereiten
    tasks = []
    
    print("Erstelle Ordnerstruktur...")
    for angle in angles:
        # Unterordner erstellen (Minuszeichen sicher im Namen verpacken)
        angle_str = str(angle).replace('-', 'minus_')
        angle_dir = os.path.join(monster_dir, f"angle_{angle_str}")
        os.makedirs(angle_dir, exist_ok=True)
        
        # Für jeden Run eine "Aufgabe" schnüren
        for i in range(1, anzahl_runs + 1):
            tasks.append((i, angle, initial_state, durchmesser, raumy, angle_dir, timestamp_main, dauer_pro_run))

    total_start = time.time()
    total_tasks = len(tasks)
    
    print(f"\n{'='*60}")
    print(f" Verteile {total_tasks} Simulationen auf 10 CPU-Kerne deines M3 Pro")
    print(f" Zurücklehnen. Das Biest arbeitet...")
    print(f"{'='*60}\n")

    # Der eigentliche Multiprocessing-Start
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        # Wir übergeben alle Aufgaben an den Pool
        futures = [executor.submit(run_single_simulation, task) for task in tasks]
        
        # Sobald EIN Kern mit SEINEM Run fertig ist, wird die Print-Meldung ausgespuckt
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
    print(f"=== MONSTER RUN BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten gespeichert in: {monster_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_batch(anzahl_runs=100, dauer_pro_run=2000.0)