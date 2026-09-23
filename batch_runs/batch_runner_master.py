# batch_runner_master.py
import sys
import os
import time
import numpy as np
import concurrent.futures

# Pfad-Fix für den Ordner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.parameters import Parameters
from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from simulation.logger import DataLogger

# --- 1. DIE FUNKTION FÜR EINEN EINZELNEN KERN ---
def run_single_simulation(args):
    (run_id, cond_name, angle, cond_g_mag, cond_actin_api, 
     cond_actin_bas, cond_actin_lat, initial_state, durchmesser, raumy, 
     cond_angle_dir, timestamp_main, dauer_pro_run) = args

    # Frisches Parameter-Objekt
    params = Parameters()
    params.raumy = raumy
    params.winkel_in_XY = angle

    # KONTROLL-PARAMETER ÜBERSCHREIBEN
    params.g_mag = cond_g_mag
    params.ACTIN_FORCE_APICAL = cond_actin_api
    params.ACTIN_FORCE_BASAL = cond_actin_bas
    params.ACTIN_LATERAL_FORCE = cond_actin_lat

    # Echte Entropie für sauberes Multiprocessing
    np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
    run_seed = np.random.randint(0, 10**9)
    np.random.seed(run_seed)
    params.current_seed = run_seed

    # Engine initialisieren
    engine = SimulationEngine(initial_state.copy(), params)

    # Logger initialisieren
    filename = os.path.join(cond_angle_dir, f"run_{run_id:03d}_{timestamp_main}.csv")
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
    return f"  -> {cond_name} | {angle}° | Run {run_id:03d} beendet in {run_duration:.1f}s"


# --- 2. DIE MULTIPROCESSING VERWALTUNG ---
def run_master_batch(anzahl_runs=100, dauer_pro_run=2000.0):
    params_base = Parameters()
    durchmesser = 25.0
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params_base.CELL_WALL
    params_base.raumy = raumy
    params_base.winkel_in_XY = 0
    
    print("--- Phase 1: Initialisiere gemeinsames Warmup ---")
    initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))

    # WINKEL FÜR DAS 1G-REFERENZFELD (15°-Schritte für perfekte Symmetrie/Polar-Plots)
    angles_1g = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]

    # ALLE EXPLORATIVEN KONDITIONEN
    conditions = [
        {
            "name": "1g_standard", 
            "g_mag": params_base.g_mag, 
            "actin_api": params_base.ACTIN_FORCE_APICAL, 
            "actin_bas": params_base.ACTIN_FORCE_BASAL, 
            "actin_lat": params_base.ACTIN_LATERAL_FORCE,
            "angles": angles_1g
        },
        {
            "name": "0g_microgravity", 
            "g_mag": 0.0, 
            "actin_api": params_base.ACTIN_FORCE_APICAL, 
            "actin_bas": params_base.ACTIN_FORCE_BASAL, 
            "actin_lat": params_base.ACTIN_LATERAL_FORCE,
            "angles": [0]
        },
        {
            "name": "2g_hypergravity", 
            "g_mag": params_base.g_mag * 2.0, 
            "actin_api": params_base.ACTIN_FORCE_APICAL, 
            "actin_bas": params_base.ACTIN_FORCE_BASAL, 
            "actin_lat": params_base.ACTIN_LATERAL_FORCE,
            "angles": [0, 90]
        },
        {
            "name": "3g_hypergravity", 
            "g_mag": params_base.g_mag * 3.0, 
            "actin_api": params_base.ACTIN_FORCE_APICAL, 
            "actin_bas": params_base.ACTIN_FORCE_BASAL, 
            "actin_lat": params_base.ACTIN_LATERAL_FORCE,
            "angles": [0, 90]
        },
        {
            "name": "1g_no_actin", 
            "g_mag": params_base.g_mag, 
            "actin_api": 0.0,
            "actin_bas": 0.0,
            "actin_lat": 0.0,
            "angles": [0, 90]
        }
    ]
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    master_dir = f"data/master_run_{timestamp_main}"
    os.makedirs(master_dir, exist_ok=True)
    
    tasks = []
    
    print("Erstelle verschachtelte Ordnerstruktur...")
    for cond in conditions:
        cond_dir = os.path.join(master_dir, cond["name"])
        
        for angle in cond["angles"]:
            angle_str = str(angle).replace('-', 'minus_')
            cond_angle_dir = os.path.join(cond_dir, f"angle_{angle_str}")
            os.makedirs(cond_angle_dir, exist_ok=True)
            
            for i in range(1, anzahl_runs + 1):
                tasks.append((
                    i, cond["name"], angle, cond["g_mag"], 
                    cond["actin_api"], cond["actin_bas"], cond["actin_lat"], 
                    initial_state, durchmesser, raumy, 
                    cond_angle_dir, timestamp_main, dauer_pro_run
                ))

    total_tasks = len(tasks)
    
    print(f"\n{'='*60}")
    print(f" Verteile {total_tasks} Simulationen auf die CPU-Kerne deines M3 Pro")
    print(f" Konditionen: Standard (1g), Micro (0g), Hyper (2g, 3g), No-Actin")
    print(f"{'='*60}\n")

    total_start = time.time()

    # Nutze max_workers=8 oder 10, je nach exaktem M3 Pro Modell (Performance/Efficiency Cores)
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_single_simulation, task) for task in tasks]
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                completed += 1
                if completed % 10 == 0 or completed == total_tasks:
                    print(f"[{completed}/{total_tasks}] {result}", flush=True)
            except Exception as exc:
                print(f"FEHLER in einem Run: {exc}")

    total_duration = (time.time() - total_start) / 3600
    print(f"\n{'='*50}")
    print(f"=== MASTER RUN BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten gespeichert in: {master_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_master_batch(anzahl_runs=100, dauer_pro_run=2000.0)