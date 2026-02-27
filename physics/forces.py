import numpy as np

def compute_forces_single(s, params):
    x, y, z, r, p_stato = s

    dist_x = params.LIMIT_X - x 
    dist_y = params.raumy - abs(y)
    dist_z = params.raumy - abs(z)
    d_wand = max(min(dist_x, dist_y, dist_z), 0)

    
    eta_eff = params.eta_parallel * (1 + np.exp(-d_wand / params.lambd))
    mobility = 1.0 / (6 * np.pi * eta_eff * r) 

    winkel1 = np.radians(params.winkel_in_XY)
    winkel2 = np.radians(params.winkel_zu_Z)

    gx = np.cos(winkel2) * np.cos(winkel1)
    gy = np.cos(winkel2) * np.sin(winkel1)
    gz = np.sin(winkel2)
    g_vec = np.array([gx, gy, gz])

    dp = (p_stato - params.p_cyto) * 1e-12

    # --- Gravitation als Vektor ---
    F_grav = (4/3) * np.pi * r**3 * dp * params.g_mag * g_vec

    # --- Actin-Potential (harmonisch entlang x) ---
    x_mid = 0.5 * (params.ACTIN_MIN_X + params.ACTIN_MAX_X)
    dx = x - x_mid
    k_actin = 1e-14
    F_actin = np.array([-k_actin * dx, 0.0, 0.0])

    # --- Zentrale harmonische Falle ---
    center = np.array([32.5, 0.0, 0.0])
    r_vec = np.array([x, y, z]) - center
    k_center = 0.1e-4
    F_center = -k_center * r_vec

    # --- Gesamtkraft ---
    F_total = F_grav + F_actin + F_center

    # --- Wand-Mobilitätskorrektur ---
    if d_wand < params.wall_layer_thickness:
        mobility *= params.wall_mobility_factor

    # --- Driftgeschwindigkeit ---
    v_total = F_total * mobility

    return v_total

