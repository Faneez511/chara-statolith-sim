import numpy as np

def compute_brownian_motion(s, params):

    x, y, z, r, _ = s

    
    dist_x = params.LIMIT_X - x
    dist_radial = params.raumy - np.sqrt(y**2 + z**2)
    d_wand = max(min(dist_x, dist_radial), 0)  

    f_wand = np.exp(-d_wand / params.lambd)
    eta_eff = params.eta_parallel * (1 + f_wand)

    wall_effect = (1.0 - params.wall_mobility_factor) * np.exp(-d_wand / (params.wall_layer_thickness / 3.0))
    mobility_factor = (1.0 - wall_effect)

    
    D = params.Kb * params.Temp / (6 * np.pi * eta_eff * r) * mobility_factor

    
    noise_vec = np.sqrt(2 * D * params.dt) * np.random.normal(0, 1, 3)

    return noise_vec