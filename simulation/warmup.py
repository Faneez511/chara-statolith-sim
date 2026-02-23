import os
import numpy as np
from config.parameters import LIMIT_X, ACTIN_DECAY_LENGTH, ACTIN_AXIAL_FORCE, ACTIN_MAX_X, ACTIN_MIN_X, ACTIN_LATERAL_FORCE, N
from geometry.cell_geometry import raumy
from ui.input_dialog import get_rhizoid_diameter

durchmesser_rhizoid = get_rhizoid_diameter()

def get_initial_state(N, durchmesser_rhizoid):
    # Dateiname enthält Parameter
    filename = f"sedimented_state_N{N}_d{int(durchmesser_rhizoid)}_v2.npy"
    
    if os.path.exists(filename):
        print(f"Lade Startzustand aus {filename}...")
        return np.load(filename)
    
    print("Berechne initiales Sedimentieren (Warm-Up Phase mit Aktin-Käfig)... bitte warten.")
    
    temp_data = []
    gen_a, gen_b, gen_c = LIMIT_X, raumy - 1.0, raumy - 1.0
    
    # Zufällige Verteilung generieren
    while len(temp_data) < N:
        d_part = np.random.uniform(0.5, 2)
        r = d_part / 2
        dichte = np.random.uniform(4.3, 4.5)
        x = np.random.uniform(0 + r, gen_a - r)
        y = np.random.uniform(-gen_b + r, gen_b - r)
        z = np.random.uniform(-gen_c + r, gen_c - r)
        if (x/gen_a)**2 + (y/gen_b)**2 + (z/gen_c)**2 <= 1:
            temp_data.append([x, y, z, r, dichte])
            
    sim_warmup = [np.array(s) for s in temp_data]
    
    dt_warm = 0.05 
    steps = 1000 
    g_warm = np.array([1, 0, 0]) * 100 * 9.81 * 1e6 
    eta_warm = 139 * 1e-6
    
    # --- WARM-UP LOOP ---
    for _ in range(steps):
        velocities = np.zeros((len(sim_warmup), 3))
        
        for i in range(len(sim_warmup)):
            s = sim_warmup[i]
            x, y, z, r, dens = s[0], s[1], s[2], s[3], s[4]
            
            # 1. Wandabstand & Mobility
            d_wand = max(min(LIMIT_X - x, raumy - abs(y), raumy - abs(z)), 0)
            eta_eff = eta_warm * (1 + np.exp(-d_wand/5))
            mobility = 1.0 / (6 * np.pi * eta_eff * r)
            
            # 2. Schwerkraft (Settling)
            dp = (dens - 1.0139) * 1e-12 #p_cyto
            velocities[i] += (4/3) * np.pi * r**3 * dp * g_warm * mobility
            
            # 3. AKTIN KRAFT (INITIALISIERUNG)
            # A) Apikale Begrenzung (wie bisher)
            dist_to_apex = ACTIN_MAX_X - x
            if 0 < dist_to_apex < 3 * ACTIN_DECAY_LENGTH:
                f_mag = ACTIN_AXIAL_FORCE * np.exp(-dist_to_apex / ACTIN_DECAY_LENGTH)
                velocities[i] += np.array([-1.0, 0.0, 0.0]) * f_mag * mobility

            # B) Basale Begrenzung (NEU!)
            dist_to_base = x - ACTIN_MIN_X
            if 0 < dist_to_base < 3 * ACTIN_DECAY_LENGTH:
                f_mag = ACTIN_AXIAL_FORCE * np.exp(-dist_to_base / ACTIN_DECAY_LENGTH)
                velocities[i] += np.array([+1.0, 0.0, 0.0]) * f_mag * mobility
            
            r_dist = np.sqrt(y**2 + z**2)
            dist_to_wall = raumy - r_dist
            if dist_to_wall < ACTIN_DECAY_LENGTH and r_dist > 0.1:
                f_lat = ACTIN_LATERAL_FORCE * np.exp(-dist_to_wall / ACTIN_DECAY_LENGTH)
                ny, nz = -y/r_dist, -z/r_dist
                velocities[i] += np.array([0.0, ny, nz]) * f_lat * mobility

        # Kollisionen
        for i in range(len(sim_warmup)):
            for j in range(i+1, len(sim_warmup)):
                dist = np.linalg.norm(sim_warmup[i][0:3] - sim_warmup[j][0:3])
                rad_sum = sim_warmup[i][3] + sim_warmup[j][3]
                if dist < rad_sum:
                    overlap = rad_sum - dist
                    n_vec = (sim_warmup[i][0:3] - sim_warmup[j][0:3]) / dist
                    corr = n_vec * overlap * 5.0 
                    velocities[i] += corr
                    velocities[j] -= corr
                    
        # Update Position Warmup
        for i in range(len(sim_warmup)):
            new_pos = sim_warmup[i][0:3] + velocities[i] * dt_warm
            val = (new_pos[0]/LIMIT_X)**2 + (new_pos[1]/raumy)**2 + (new_pos[2]/raumy)**2
            if val > 0.95:
                 norm_vec = -new_pos / np.linalg.norm(new_pos)
                 new_pos += norm_vec * (val - 0.95) * 10.0
            if new_pos[0] < r:
                new_pos[0] = r
            elif new_pos[0] > LIMIT_X - r:
                new_pos[0] = LIMIT_X - r
            sim_warmup[i][0:3] = new_pos

    print("Sedimentierung abgeschlossen. Speichere Zustand.")
    final_data = [list(s) for s in sim_warmup]
    np.save(filename, final_data)
    return final_data