# batch_runner.py
import numpy as np
import time
import os
from config.parameters import Parameters
from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from simulation.logger import DataLogger

def run_batch(anzahl_runs=100, dauer_pro_run=600.0):
    params = Parameters()
    durchmesser = 25.0 # Standardwert
    
    # 1. Warmup einmalig holen/erstellen
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params.CELL_WALL
    params.raumy = raumy
    
    print("--- Phase 1: Initialisiere/Lade Warmup ---")
    # Der Warmup-Code nutzt intern seine eigenen Zufallswerte (eigener Seed-Zustand)
    initial_state = np.array(get_initial_state(params.N, durchmesser, raumy, params))

    print(f"--- Phase 2: Starte {anzahl_runs} Batch-Runs ---")
    
    for i in range(1, anzahl_runs + 1):
        # Einzigartigen Seed für diesen spezifischen Run generieren
        run_seed = np.random.randint(0, 10**9)
        np.random.seed(run_seed)
        params.current_seed = run_seed # Im Parameter-Objekt speichern
        
        # Engine mit dem IMMER GLEICHEN initial_state starten
        engine = SimulationEngine(initial_state, params)
        
        # Logger mit Zeitstempel und Seed initialisieren
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"data/run_{i:03d}_{timestamp}.csv"
        logger = DataLogger(filename, params, durchmesser, run_seed)
        
        sim_time = 0.0
        log_interval = 0.1
        next_log = 0.0
        
        print(f"Run {i}/{anzahl_runs} gestartet (Seed: {run_seed})...")
        
        # Simulations-Schleife ohne Grafik (Headless)
        while sim_time < dauer_pro_run:
            engine.step(params.dt)
            sim_time += params.dt
            
            if sim_time >= next_log:
                logger.log(sim_time, engine.state)
                next_log += log_interval
                
        print(f"Run {i} nach {sim_time:.1f}s beendet.")

if __name__ == "__main__":
    run_batch(anzahl_runs=100, dauer_pro_run=600.0)