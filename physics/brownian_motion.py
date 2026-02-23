import numpy as np

def compute_brownian_motion(s, params):

    x, y, z, r, _ = s

    
    dist_x = params.LIMIT_X - x
    dist_y = params.raumy - abs(y)
    dist_z = params.raumy - abs(z)
    d_wand = max(min(dist_x, dist_y, dist_z), 0)

    f_wand = np.exp(-d_wand / params.lambd)
    eta_eff = params.eta_parallel * (1 + f_wand)

    
    D = params.Kb * params.Temp / (6 * np.pi * eta_eff * r)

    
    noise_vec = np.sqrt(2 * D * params.dt) * np.random.normal(0, 1, 3)

    return noise_vec