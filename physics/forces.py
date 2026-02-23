import numpy as np

def compute_forces_single(s, params):
    x, y, z, r, p_stato = s

    dist_x = params.LIMIT_X - x 
    dist_y = params.raumy - abs(y)
    dist_z = params.raumy - abs(z)
    d_wand = max(min(dist_x, dist_y, dist_z), 0)

    f_wand = np.exp(-d_wand / params.lambd)
    eta_eff = params.eta_parallel * (1 + f_wand)
    mobility = 1.0 / (6 * np.pi * eta_eff * r) 

    dp = (p_stato - params.p_cyto) * 1e-12
    F_grav_mag = (4/3) * np.pi * r**3 * dp * params.g_mag
    v_sed_vec = F_grav_mag * mobility * params.g_vec 

    shield = 1.0
    if params.ACTIN_MIN_X <= x <= params.ACTIN_MAX_X:
        shield = 0.3

    v_total = v_sed_vec * shield

    x_mid = 0.5 * (params.ACTIN_MIN_X + params.ACTIN_MAX_X)
    dx = x - x_mid
    k_actin = 2e-10
    F_actin_x = -k_actin * dx

    v_total[0] += F_actin_x * mobility

    return v_total