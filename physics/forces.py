import numpy as np

def compute_forces_single(s, params):
    x, y, z, r, p_stato = s

    # --- 0. LOKALE GEOMETRIE (ELLIPSOID) BERECHNEN ---
    x_safe = min(max(x, 0.0), params.TIP_POSITION_X)
    
    # Der wahre Radius der Zelle an der Position X
    local_raumy = params.raumy * np.sqrt(1.0 - (x_safe / params.TIP_POSITION_X)**2)
    
    # Abstand von der zentralen Achse
    r_dist = np.sqrt(y**2 + z**2)
    
    # Wahrer Abstand zur gekrümmten Zellwand (Nutzen wir für Viskosität UND Aktin)
    # Wahrer Abstand der Partikel-Oberfläche zur gekrümmten Zellwand
    dist_radial = local_raumy - r_dist - r

    # --- 1. WANDABSTAND & EFFEKTIVE VISKOSITÄT ---
    dist_x_apikal = params.LIMIT_X - x - r
    dist_x_basal = x - params.ACTIN_MIN_X - r
    d_wand = max(min(dist_x_apikal, dist_x_basal, dist_radial), 0)

    eta_eff = params.eta_parallel * (1 + np.exp(-d_wand / params.lambd))
    mobility = 1.0 / (6 * np.pi * eta_eff * r)
    
    # Weicher, exponentieller Übergang für die Wandreibung
    wall_effect = (1.0 - params.wall_mobility_factor) * np.exp(-d_wand / (params.wall_layer_thickness / 3.0))
    mobility *= (1.0 - wall_effect)

    # --- 2. GRAVITATION ---
    # Quelle: Stokes-Sedimentation, Braun et al. 2002
    winkel1 = np.radians(params.winkel_in_XY)
    winkel2 = np.radians(params.winkel_zu_Z)
    gx = np.cos(winkel2) * np.cos(winkel1)
    gy = np.cos(winkel2) * np.sin(winkel1)
    gz = np.sin(winkel2)
    g_vec = np.array([gx, gy, gz])
    dp = (p_stato - params.p_cyto)
    F_grav = (4/3) * np.pi * r**3 * dp * params.g_mag * g_vec

    # --- 3. ACTIN AXIAL (Asymmetrisch nach Braun 2001) ---
    F_actin = np.array([0.0, 0.0, 0.0])

    # Apikale Wand (100% Laser-Power)
    dist_to_apex = params.ACTIN_MAX_X - x
    if dist_to_apex < 3 * params.ACTIN_DECAY_APICAL:
        f_mag = params.ACTIN_FORCE_APICAL * np.exp(-dist_to_apex / params.ACTIN_DECAY_APICAL)
        F_actin[0] -= f_mag  # weg von Apex

    # Basale Wand (35% Laser-Power)
    dist_to_base = x - params.ACTIN_MIN_X
    if dist_to_base < 3 * params.ACTIN_DECAY_BASAL:
        f_mag = params.ACTIN_FORCE_BASAL * np.exp(-dist_to_base / params.ACTIN_DECAY_BASAL)
        F_actin[0] += f_mag  # weg von Basis

    # --- 4. ACTIN LATERAL ---
    # Nutzt jetzt den echten Abstand zur gekrümmten Wand (dist_radial)
    F_lateral = np.array([0.0, 0.0, 0.0])
    if dist_radial < params.ACTIN_DECAY_LENGTH and r_dist > 0.1:
        f_lat = params.ACTIN_LATERAL_FORCE * np.exp(-dist_radial / params.ACTIN_DECAY_LENGTH)
        F_lateral[1] = -f_lat * (y / r_dist)
        F_lateral[2] = -f_lat * (z / r_dist)

    # --- GESAMTKRAFT ---
    F_total = F_grav + F_actin + F_lateral

    return F_total * mobility