import csv
import os
import time
import numpy as np

class DataLogger:
    def __init__(self, filename, params, rhizoid_diameter, seed):
        self.filename = filename
        
        # Header mit allen wichtigen Metadaten für dein Paper
        header_lines = [
            f"# Chara Statolith Simulation - Rohdaten",
            f"# Erstellt am: {time.strftime('%d.%m.%Y %H:%M:%S')}",
            f"# --------------------------------------------------",
            f"# PARAMETER:",
            f"# Seed: {seed}",
            f"# Anzahl Statolithen (N): {params.N}",
            f"# Rhizoid-Durchmesser: {rhizoid_diameter} um",
            f"# Actin Decay Length (lambda): {params.ACTIN_DECAY_LENGTH} um",
            f"# LJ Epsilon (Klebrigkeit): {params.lj_eps}",
            f"# Viskosität (eta): {params.eta_parallel}",
            f"# Winkel XY / Z: {params.winkel_in_XY}° / {params.winkel_zu_Z}°",
            f"# --------------------------------------------------"
        ]
        
        with open(self.filename, mode='w', newline='') as f:
            # Metadaten als Kommentare schreiben
            for line in header_lines:
                f.write(line + "\n")
            
            # Spaltenüberschriften
            writer = csv.writer(f)
            writer.writerow([
            "time_s", "com_x", "com_y", "com_z", 
            "v_x", "v_y", "v_z", 
            "std_x", "std_y", "std_z", "contacts"
        ])

    def log(self, sim_time, engine):
    # Wir übergeben jetzt die ganze engine, um auf v und contacts zuzugreifen
        pos = engine.state[:, :3]
        com = np.mean(pos, axis=0)
        std = np.std(pos, axis=0)
        vels = engine.get_current_velocities()
        contacts = engine.get_contact_count()
        
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                round(sim_time, 4),
                round(com[0], 6), round(com[1], 6), round(com[2], 6),
                round(vels[0], 8), round(vels[1], 8), round(vels[2], 8),
                round(std[0], 6), round(std[1], 6), round(std[2], 6),
                contacts
            ])