# simulation/warmup.py
import os
import numpy as np
from physics.constraints import apply_constraints
from physics.forces import compute_forces_single

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
    
    filename = os.path.join(
        base_dir,
        f"sedimented_state_N{N}_d{durchmesser_rhizoid:.1f}_v2.npy"
    )

    if os.path.exists(filename):
        print(f"Lade Startzustand aus {filename}...")
        return np.load(filename, allow_pickle=True)

    print(f"Keine Datei für Durchmesser {durchmesser_rhizoid} µm gefunden, berechne Warmup...")
    
    # --- WICHTIG: Winkel für das Warmup zwingend auf 0° (Senkrecht) setzen ---
    # Wir speichern deine eigentlichen Einstellungen zwischen
    original_winkel_in_XY = params.winkel_in_XY
    original_winkel_zu_Z = params.winkel_zu_Z
    
    # Zwinge die Gravitation für den Fall exakt in Richtung der Spitze (+X)
    params.winkel_in_XY = 0
    params.winkel_zu_Z = 0
    
    # --- Warmup-Code ---
    print("Berechne initiales Sedimentieren (Warm-Up Phase mit voller Physik-Engine)... bitte warten.")
    
    temp_data = []
    gen_a = params.LIMIT_X
    
    while len(temp_data) < N:
        d_part = np.random.uniform(0.5, 2)
        r = d_part / 2
        dichte = np.random.uniform(4.3, 4.5) # effektive vesikel dichte 1993 braun und sievers
        
        # X-Position sicher im Subapikalen Bereich generieren
        x = np.random.uniform(max(r, params.ACTIN_MIN_X + r), gen_a - r)
        y = np.random.uniform(-raumy + r, raumy - r)
        z = np.random.uniform(-raumy + r, raumy - r)
        
        # Lokalen Radius am Punkt X berechnen (Ellipsoid-Gleichung)
        x_safe = min(max(x, 0.0), params.TIP_POSITION_X)
        local_raumy = params.raumy * np.sqrt(1.0 - (x_safe / params.TIP_POSITION_X)**2)
        
        # Nur spawnen, wenn das Partikel strikt im lokalen Ellipsoid liegt
        if np.sqrt(y**2 + z**2) <= (local_raumy - r):
            temp_data.append([x, y, z, r, dichte])
            print(f"Partikel {len(temp_data)}: x={x:.2f}, y={y:.2f}, z={z:.2f}, r={r:.2f}")

    print(f"Anzahl erzeugter Partikel: {len(temp_data)}")
    sim_warmup = [np.array(s) for s in temp_data]

    dt_warm = 0.05
    steps = 10000

    # --- WARM-UP LOOP (Nutzt exakt dieselbe Physik wie engine.py!) ---
    for step in range(steps):
        velocities = np.zeros((len(sim_warmup), 3))

        # 1. Alle externen Kräfte berechnen (via forces.py)
        # Da wir params.winkel... oben auf 0 gesetzt haben, zieht forces.py jetzt perfekt in +X Richtung
        for i in range(len(sim_warmup)):
            velocities[i] += compute_forces_single(sim_warmup[i], params)

        # 2. Lennard-Jones Interaktionen (Exakt wie in engine.py - zieht Partikel sanft zusammen)
        for i in range(len(sim_warmup)):
            for j in range(i + 1, len(sim_warmup)):
                rij = sim_warmup[j][0:3] - sim_warmup[i][0:3]
                dist = np.linalg.norm(rij)
                
                if dist < 1e-10 or dist > params.lj_cutoff:
                    continue
                
                sig = params.lj_sigma  
                eps = params.lj_eps    

                dist_eff = max(dist, 0.8 * sig)
                sr6 = (sig / dist_eff) ** 6
                f_mag = 24 * eps * (2 * sr6**2 - sr6) / dist_eff
                f_mag = np.clip(f_mag, -1e-2, 1e-2)
                
                ri = sim_warmup[i][3]
                rj = sim_warmup[j][3]
                mob_i = 1.0 / (6 * np.pi * params.eta_parallel * ri)
                mob_j = 1.0 / (6 * np.pi * params.eta_parallel * rj)
                
                f_vec = f_mag * (rij / dist)
                velocities[i] -= f_vec * mob_i
                velocities[j] += f_vec * mob_j

        # 3. Velocity Clipping (Verhindert Explosionen, exakt wie in engine.py)
        for i in range(len(velocities)):
            v = velocities[i]
            v_mag = np.linalg.norm(v)
            dist_step = v_mag * dt_warm
            
            if dist_step > params.MAX_STEP:
                scale = params.MAX_STEP / dist_step
                velocities[i] *= scale

        # 4. Positionen updaten und Constraints anwenden
        for i in range(len(sim_warmup)):
            sim_warmup[i][0:3] += velocities[i] * dt_warm
            # Nutzt exakt dein neues Constraint-Modul für perfekte Geometrie
            sim_warmup[i][0:3] = apply_constraints(sim_warmup[i][0:3], sim_warmup[i][3], params)
            
        # Terminal-Output alle 1000 Schritte zur Überwachung
        if (step + 1) % 1000 == 0:
            print(f"Warmup Fortschritt: {step + 1}/{steps} Schritte")

    # --- FINALE CONSTRAINTS ---
    print("Finale Constraints anwenden...")
    for i in range(len(sim_warmup)):
        sim_warmup[i][0:3] = apply_constraints(sim_warmup[i][0:3], sim_warmup[i][3], params)

    print("Sedimentierung abgeschlossen. Speichere Zustand.")
    final_data = [list(s) for s in sim_warmup]
    np.save(filename, final_data)
    
    # --- WICHTIG: Winkel für die Main-Simulation wiederherstellen ---
    params.winkel_in_XY = original_winkel_in_XY
    params.winkel_zu_Z = original_winkel_zu_Z
    
    return final_data