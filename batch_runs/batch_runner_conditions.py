# batch_runner_v3.py
import numpy as np
import time
import os
from datetime import datetime
from config.parameters import Parameters
from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from simulation.logger import DataLogger

def run_batch_v3(anzahl_runs=100, dauer_pro_run=2000.0):
    # 1. Gemeinsames Warmup holen (gleiche Basis wie bei den Winkel-Runs!)
    params_base = Parameters()
    durchmesser = 25.0
    mittelpunkt = durchmesser / 2.0
    raumy = mittelpunkt - params_base.CELL_WALL
    params_base.raumy = raumy
    params_base.winkel_in_XY = 0  # Standardwinkel (0 Grad) für den Startzustand
    
    print("--- Phase 1: Initialisiere/Lade gemeinsames Warmup (Basis) ---")
    initial_state = np.array(get_initial_state(params_base.N, durchmesser, raumy, params_base))

    # 2. Die Kontroll-Bedingungen definieren (Monster-Run V3)
    conditions = [
        {
            "name": "0g_microgravity", 
            "g_mag": 0.0, 
            "actin_max": params_base.ACTIN_MAX_FORCE, 
            "actin_lat": params_base.ACTIN_LATERAL_FORCE,
            "limit_x": params_base.LIMIT_X,  # Bleibt bei 45.0
            "desc": "Weltraum-Bedingung: Schwerkraft aus, Actin bleibt intakt."
        },
        {
            "name": "no_actin", 
            "g_mag": params_base.g_mag, 
            "actin_max": 0.0, 
            "actin_lat": 0.0,
            "limit_x": 50.0,
            "desc": "Cytochalasin-D-Szenario: Normale Schwerkraft, aber Actin-Kräfte zerstört."
        }
    ]
    
    print(f"--- Phase 2: Starte Monster-Run V3 für {len(conditions)} Kontrollbedingungen ---")
    
    timestamp_main = time.strftime("%Y%m%d_%H%M%S")
    monster_dir = f"data/monster_run_v3_{timestamp_main}"
    os.makedirs(monster_dir, exist_ok=True)
    
    total_start = time.time()

    for cond in conditions:
        print(f"\n{'='*60}")
        print(f" Starte Batch für Bedingung: {cond['name']}")
        print(f" ({cond['desc']})")
        print(f"{'='*60}")
        
        # Unterordner erstellen
        cond_dir = os.path.join(monster_dir, cond["name"])
        os.makedirs(cond_dir, exist_ok=True)
        
        for i in range(1, anzahl_runs + 1):
            run_start = time.time()
            
            # Parameter für diesen Run neu aufsetzen
            params = Parameters()
            params.raumy = raumy
            params.winkel_in_XY = 0  # Wir testen beide Kontrollen als Referenz bei 0° (vertikal)
            
            # ---> HIER WERDEN DIE KONTROLL-PARAMETER ÜBERSCHRIEBEN <---
            params.g_mag = cond["g_mag"]
            params.ACTIN_MAX_FORCE = cond["actin_max"]
            params.ACTIN_LATERAL_FORCE = cond["actin_lat"]
            
            # Geometrische Grenze für das No-Actin Szenario aufheben
            params.LIMIT_X = cond["limit_x"]
            params.ACTIN_MAX_X = cond["limit_x"]
            
            # Einzigartigen Seed generieren
            run_seed = np.random.randint(0, 10**9)
            np.random.seed(run_seed)
            params.current_seed = run_seed
            
            # WICHTIG: .copy() verhindert, dass der gemeinsame Startzustand überschrieben wird
            engine = SimulationEngine(initial_state.copy(), params)
            
            # Logger initialisieren
            filename = os.path.join(cond_dir, f"run_{i:03d}_{timestamp_main}.csv")
            logger = DataLogger(filename, params, durchmesser, run_seed)
            
            sim_time = 0.0
            log_interval = 0.1
            next_log = 0.0
            
            print(f"  -> {cond['name']:<15} | Run {i}/{anzahl_runs} (Seed: {run_seed}) läuft... ", end="", flush=True)
            
            # Simulations-Schleife
            while sim_time < dauer_pro_run:
                engine.step(params.dt)
                sim_time += params.dt
                
                if sim_time >= next_log:
                    logger.log(sim_time, engine)
                    next_log += log_interval
                    
            run_duration = time.time() - run_start
            print(f"Fertig in {run_duration:.1f}s")

    total_duration = (time.time() - total_start) / 3600
    print(f"\n{'='*60}")
    print(f"=== MONSTER RUN V3 BEENDET ===")
    print(f"Gesamtdauer: {total_duration:.2f} Stunden")
    print(f"Alle Daten gespeichert in: {monster_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_batch_v3(anzahl_runs=100, dauer_pro_run=2000.0)