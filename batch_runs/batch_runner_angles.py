# batch_runner.py
import numpy as np
import time
import os
from datetime import datetime
from config.parameters import Parameters
from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from simulation.logger import DataLogger

def run_batch(anzahl_runs=100, dauer_pro_run=2000.0):
    # 1. Gemeinsames Warmup holen
    params_base = Parameters()
    durchmesser = 25.0
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params_base.CELL_WALL
    params_base.raumy = raumy
    
    print("--- Phase 1: Initialisiere/Lade gemeinsames Warmup ---")
    initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))

    # 2. Die perfekten Winkel
    angles = [0, 45, 90, -90, 180]
    
    print(f"--- Phase 2: Starte Monster-Run für {len(angles)} Winkel ---")
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    monster_dir = f"data/monster_run_{timestamp_main}"
    os.makedirs(monster_dir, exist_ok=True)
    
    total_start = time.time()

    for angle in angles:
        print(f"\n{'='*50}")
        print(f" Starte Batch für Winkel: {angle}°")
        print(f"{'='*50}")
        
        # Unterordner erstellen (Minuszeichen sicher im Namen verpacken)
        angle_str = str(angle).replace('-', 'minus_')
        angle_dir = os.path.join(monster_dir, f"angle_{angle_str}")
        os.makedirs(angle_dir, exist_ok=True)
        
        for i in range(1, anzahl_runs + 1):
            run_start = time.time()
            
            # Parameter für diesen Run neu aufsetzen
            params = Parameters()
            params.raumy = raumy
            params.winkel_in_XY = angle  # <--- HIER WIRD DER WINKEL GESETZT!
            
            # Einzigartigen Seed generieren
            run_seed = np.random.randint(0, 10**9)
            np.random.seed(run_seed)
            params.current_seed = run_seed
            
            # WICHTIG: .copy() verhindert, dass der Startzustand überschrieben wird
            engine = SimulationEngine(initial_state.copy(), params)
            
            # Logger initialisieren
            filename = os.path.join(angle_dir, f"run_{i:03d}_{timestamp_main}.csv")
            logger = DataLogger(filename, params, durchmesser, run_seed)
            
            sim_time = 0.0
            log_interval = 0.1
            next_log = 0.0
            
            print(f"  -> {angle}° | Run {i}/{anzahl_runs} (Seed: {run_seed}) läuft... ", end="", flush=True)
            
            # Simulations-Schleife (100 % identisch zu vorher)
            while sim_time < dauer_pro_run:
                engine.step(params.dt)
                sim_time += params.dt
                
                if sim_time >= next_log:
                    logger.log(sim_time, engine)
                    next_log += log_interval
                    
            run_duration = time.time() - run_start
            print(f"Fertig in {run_duration:.1f}s")

    total_duration = (time.time() - total_start) / 3600
    print(f"\n{'='*50}")
    print(f"=== MONSTER RUN BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten gespeichert in: {monster_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_batch(anzahl_runs=100, dauer_pro_run=2000.0)