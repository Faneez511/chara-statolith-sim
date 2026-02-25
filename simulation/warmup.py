# simulation/warmup.py
import os
import numpy as np

def get_initial_state(N, durchmesser_rhizoid, raumy, params):
    """
    Generiert den Startzustand der Statolithen.
    Wenn Datei existiert, lädt sie; sonst Sedimentierung (Warmup).
    
    Parameter:
    N                 : Anzahl der Partikel
    durchmesser_rhizoid : Rhizoid-Durchmesser (µm)
    raumy             : halber Zellradius in y/z Richtung
    params            : Parameters-Objekt mit allen Konstanten
    """

    # --- Pfad immer relativ zu diesem Script ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Dateiname hängt jetzt von allen relevanten Parametern ab (N und Durchmesser)
    filename = os.path.join(
        base_dir,
        f"sedimented_state_N{N}_d{durchmesser_rhizoid:.1f}_v2.npy"
    )

    if os.path.exists(filename):
        print(f"Lade Startzustand aus {filename}...")
        return np.load(filename, allow_pickle=True)

    print(f"Keine Datei für Durchmesser {durchmesser_rhizoid} µm gefunden, berechne Warmup...")
    
    # --- Warmup-Code ---
    print("Berechne initiales Sedimentieren (Warm-Up Phase mit Aktin-Käfig)... bitte warten.")
    
    temp_data = []
    gen_a, gen_b, gen_c = params.LIMIT_X, raumy - 1.0, raumy - 1.0
    
    while len(temp_data) < N:
        d_part = np.random.uniform(0.5, 2)
        r = d_part / 2
        dichte = np.random.uniform(4.3, 4.5)
        x = np.random.uniform(r, gen_a - r)
        y = np.random.uniform(-gen_b + r, gen_b - r)
        z = np.random.uniform(-gen_c + r, gen_c - r)
        if (x/gen_a)**2 + (y/gen_b)**2 + (z/gen_c)**2 <= 1.0:
            temp_data.append([x, y, z, r, dichte])
            print(f"Partikel {len(temp_data)}: x={x:.2f}, y={y:.2f}, z={z:.2f}, r={r:.2f}")

    print(f"Anzahl erzeugter Partikel: {len(temp_data)}")
    sim_warmup = [np.array(s) for s in temp_data]

    dt_warm = 0.05
    steps = 1000
    g_warm = np.array([1, 0, 0]) * 100 * params.g_mag
    eta_warm = 139e-6

    # --- WARM-UP LOOP ---
    for _ in range(steps):
        velocities = np.zeros((len(sim_warmup), 3))

        for i in range(len(sim_warmup)):
            s = sim_warmup[i]
            x, y, z, r, dens = s

            # Wandabstand & Mobility
            d_wand = max(min(params.LIMIT_X - x, raumy - abs(y), raumy - abs(z)), 0)
            eta_eff = eta_warm * (1 + np.exp(-d_wand / 5))
            mobility = 1.0 / (6 * np.pi * eta_eff * r)

            # Schwerkraft
            dp = (dens - params.p_cyto) * 1e-12
            velocities[i] += (4/3) * np.pi * r**3 * dp * g_warm * mobility

            # Aktin-Kräfte (apikal + basal + lateral)
            dist_to_apex = params.ACTIN_MAX_X - x
            if 0 < dist_to_apex < 3 * params.ACTIN_DECAY_LENGTH:
                f_mag = params.ACTIN_AXIAL_FORCE * np.exp(-dist_to_apex / params.ACTIN_DECAY_LENGTH)
                velocities[i] += np.array([-1.0, 0.0, 0.0]) * f_mag * mobility

            dist_to_base = x - params.ACTIN_MIN_X
            if 0 < dist_to_base < 3 * params.ACTIN_DECAY_LENGTH:
                f_mag = params.ACTIN_AXIAL_FORCE * np.exp(-dist_to_base / params.ACTIN_DECAY_LENGTH)
                velocities[i] += np.array([1.0, 0.0, 0.0]) * f_mag * mobility

            r_dist = np.sqrt(y**2 + z**2)
            dist_to_wall = raumy - r_dist
            if dist_to_wall < params.ACTIN_DECAY_LENGTH and r_dist > 0.1:
                f_lat = params.ACTIN_LATERAL_FORCE * np.exp(-dist_to_wall / params.ACTIN_DECAY_LENGTH)
                ny, nz = -y/r_dist, -z/r_dist
                velocities[i] += np.array([0.0, ny, nz]) * f_lat * mobility

        # Kollisionen
        for i in range(len(sim_warmup)):
            for j in range(i + 1, len(sim_warmup)):
                dist = np.linalg.norm(sim_warmup[i][0:3] - sim_warmup[j][0:3])
                rad_sum = sim_warmup[i][3] + sim_warmup[j][3]
                if dist < rad_sum:
                    overlap = rad_sum - dist
                    n_vec = (sim_warmup[i][0:3] - sim_warmup[j][0:3]) / dist
                    corr = n_vec * overlap * 5.0
                    velocities[i] += corr
                    velocities[j] -= corr

        # Update Positionen mit Hard Constraints
        for i in range(len(sim_warmup)):
            sim_warmup[i][0:3] += velocities[i] * dt_warm
            

    print("Sedimentierung abgeschlossen. Speichere Zustand.")
    final_data = [list(s) for s in sim_warmup]
    np.save(filename, final_data)
    return final_data