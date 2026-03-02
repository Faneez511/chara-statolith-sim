import numpy as np

def compute_forces_single(s, params):
    x, y, z, r, p_stato = s

    # --- Wandabstand & effektive Viskosität ---
    dist_x = params.LIMIT_X - x
    dist_radial = params.raumy - np.sqrt(y**2 + z**2)
    d_wand = max(min(dist_x, dist_radial), 0)

    eta_eff = params.eta_parallel * (1 + np.exp(-d_wand / params.lambd))
    mobility = 1.0 / (6 * np.pi * eta_eff * r)
    
    # Weicher, exponentieller Übergang für die Wandreibung (keine harte Kante!)
    wall_effect = (1.0 - params.wall_mobility_factor) * np.exp(-d_wand / (params.wall_layer_thickness / 3.0))
    mobility *= (1.0 - wall_effect)

    # --- 1. GRAVITATION ---
    # Quelle: Stokes-Sedimentation, Braun et al. 2002
    winkel1 = np.radians(params.winkel_in_XY)
    winkel2 = np.radians(params.winkel_zu_Z)
    gx = np.cos(winkel2) * np.cos(winkel1)
    gy = np.cos(winkel2) * np.sin(winkel1)
    gz = np.sin(winkel2)
    g_vec = np.array([gx, gy, gz])
    dp = (p_stato - params.p_cyto) * 1e-12
    F_grav = (4/3) * np.pi * r**3 * dp * params.g_mag * g_vec

    # --- 2. ACTIN AXIAL (apikal + basal) ---
    # Exponentieller Käfig: hält Statolithen zwischen ACTIN_MIN_X und ACTIN_MAX_X
    # Quelle: Volkmann et al. 1999 - subapikale Actin-Zone
    F_actin = np.array([0.0, 0.0, 0.0])

    dist_to_apex = params.ACTIN_MAX_X - x
    if dist_to_apex < 3 * params.ACTIN_DECAY_LENGTH:
        f_mag = params.ACTIN_MAX_FORCE * np.exp(-dist_to_apex / params.ACTIN_DECAY_LENGTH)
        F_actin[0] -= f_mag  # weg von Apex

    dist_to_base = x - params.ACTIN_MIN_X
    if dist_to_base < 3 * params.ACTIN_DECAY_LENGTH:
        f_mag = params.ACTIN_MAX_FORCE * np.exp(-dist_to_base / params.ACTIN_DECAY_LENGTH)
        F_actin[0] += f_mag  # weg von Basis

    # --- 3. ACTIN LATERAL ---
    # Hält Statolithen von Zellwand weg (nicht zur Achse hin!)
    # Quelle: Braun & Wasteneys 1998 - kortikales Actin
    r_dist = np.sqrt(y**2 + z**2)
    dist_to_wall = params.raumy - r_dist
    F_lateral = np.array([0.0, 0.0, 0.0])
    if dist_to_wall < params.ACTIN_DECAY_LENGTH and r_dist > 0.1:
        f_lat = params.ACTIN_LATERAL_FORCE * np.exp(-dist_to_wall / params.ACTIN_DECAY_LENGTH)
        F_lateral[1] = -f_lat * (y / r_dist)
        F_lateral[2] = -f_lat * (z / r_dist)

    # --- GESAMTKRAFT ---
    F_total = F_grav + F_actin + F_lateral

    return F_total * mobility