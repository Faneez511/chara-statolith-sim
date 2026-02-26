import numpy as np

def compute_forces_single(s, params):
    x, y, z, r, p_stato = s

    dist_x = params.LIMIT_X - x 
    dist_y = params.raumy - abs(y)
    dist_z = params.raumy - abs(z)
    d_wand = max(min(dist_x, dist_y, dist_z), 0)

    f_wand = np.exp(-d_wand / params.lambd)
    eta_eff = params.eta_parallel * (1 + np.exp(-d_wand / params.lambd))
    mobility = 1.0 / (6 * np.pi * eta_eff * r) 

    winkel1 = np.radians(params.winkel_in_XY)
    winkel2 = np.radians(params.winkel_zu_Z)

    gx = np.cos(winkel2) * np.cos(winkel1)
    gy = np.cos(winkel2) * np.sin(winkel1)
    gz = np.sin(winkel2)
    g_vec = np.array([gx, gy, gz])

    dp = (p_stato - params.p_cyto) * 1e-12
    F_grav_mag = (4/3) * np.pi * r**3 * dp * params.g_mag
    v_sed_vec = F_grav_mag * mobility * g_vec 

    v_total = v_sed_vec

    x_mid = 0.5 * (params.ACTIN_MIN_X + params.ACTIN_MAX_X)
    dx = x - x_mid
    k_actin = 1e-14
    F_actin_x = -k_actin * dx 

    v_total[0] += F_actin_x * mobility

    # Mittelpunkt der gravisensitiven Zone
    center = np.array([32.5, 0.0, 0.0])
    r_vec = s[0:3] - center
    F_center_strength = 0.1e-4
    F_center = -F_center_strength * r_vec
    v_total += F_center * mobility

    return v_total

