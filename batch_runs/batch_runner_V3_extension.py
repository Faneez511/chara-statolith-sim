import sys
import os
import time
import numpy as np
import concurrent.futures

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.parameters import Parameters
from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from simulation.logger import DataLogger

# ==========================================
# WICHTIG: TRAGE HIER DEINEN BESTEHENDEN ORDNER EIN!
# ==========================================
EXISTING_MONSTER_DIR = "data/monster_run_v3_20260403_223101"


# --- 1. DIE FUNKTION FÜR EINEN EINZELNEN KERN ---
def run_single_simulation(args):
    (run_id, cond_name, angle, cond_g_mag, cond_actin_api, 
     cond_actin_bas, cond_actin_lat, initial_state, durchmesser, raumy, 
     cond_angle_dir, timestamp_main, dauer_pro_run) = args

    params = Parameters()
    params.raumy = raumy
    params.winkel_in_XY = angle

    params.g_mag = cond_g_mag
    params.ACTIN_FORCE_APICAL = cond_actin_api
    params.ACTIN_FORCE_BASAL = cond_actin_bas
    params.ACTIN_LATERAL_FORCE = cond_actin_lat

    np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
    run_seed = np.random.randint(0, 10**9)
    np.random.seed(run_seed)
    params.current_seed = run_seed

    engine = SimulationEngine(initial_state.copy(), params)

    # Dateinamen generieren (mit neuem Zeitstempel, damit nichts überschrieben wird)
    filename = os.path.join(cond_angle_dir, f"run_{run_id:03d}_{timestamp_main}.csv")
    logger = DataLogger(filename, params, durchmesser, run_seed)

    sim_time = 0.0
    log_interval = 0.1
    next_log = 0.0
    run_start = time.time()

    while sim_time < dauer_pro_run:
        engine.step(params.dt)
        sim_time += params.dt
        
        if sim_time >= next_log:
            logger.log(sim_time, engine)
            next_log += log_interval

    run_duration = time.time() - run_start
    return f"  -> {cond_name} | {angle}° | Run {run_id:03d} (Seed: {run_seed}) gespeichert in {run_duration:.1f}s"


# --- 2. DIE MULTIPROCESSING VERWALTUNG ---
def run_batch_v3_extension(anzahl_runs=100, dauer_pro_run=2000.0):
    if not os.path.exists(EXISTING_MONSTER_DIR):
        print(f"FEHLER: Der Ordner {EXISTING_MONSTER_DIR} wurde nicht gefunden!")
        return

    params_base = Parameters()
    durchmesser = 25.0
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params_base.CELL_WALL
    params_base.raumy = raumy
    params_base.winkel_in_XY = 0
    
    print("--- Phase 1: Lade gemeinsames Warmup (Basis) ---")
    initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))

    # Nur noch die fehlenden Zwischenwinkel für No-Actin
    conditions = [
        {
            "name": "no_actin", 
            "g_mag": params_base.g_mag, 
            "actin_api": 0.0,
            "actin_bas": 0.0,
            "actin_lat": 0.0,
            "angles": [15, 30, 45, 60, 75]
        }
    ]
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    tasks = []
    
    print(f"Füge neue Winkel zum bestehenden Ordner {EXISTING_MONSTER_DIR} hinzu...")
    for cond in conditions:
        cond_name = cond["name"]
        cond_dir = os.path.join(EXISTING_MONSTER_DIR, cond_name)
        
        for angle in cond["angles"]:
            angle_str = str(angle).replace('-', 'minus_')
            cond_angle_dir = os.path.join(cond_dir, f"angle_{angle_str}")
            os.makedirs(cond_angle_dir, exist_ok=True) # Erstellt den Ordner, falls er nicht existiert
            
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
    print(f" Verteile {total_tasks} zusätzliche Simulationen auf 8 CPU-Kerne")
    print(f"{'='*60}\n")

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
    print(f"=== ERWEITERUNG BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten in {EXISTING_MONSTER_DIR} ergänzt.")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_batch_v3_extension(anzahl_runs=100, dauer_pro_run=2000.0)