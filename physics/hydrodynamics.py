import numpy as np

def get_local_mobility(pos, radius, params):
    """
    Zentrale Berechnung der Mobilität (mu) nach dem 
    Fluktuations-Dissipations-Theorem.
    """
    pos = np.atleast_2d(pos)
    x = pos[:, 0]
    y = pos[:, 1]
    z = pos[:, 2]
    
    # 1. Distanzen zur Wand INKLUSIVE Partikelradius berechnen
    dist_apical = params.TIP_POSITION_X - x - radius
    dist_basal = x - params.ACTIN_MIN_X - radius
    
    # Radiale Distanz zur gekrümmten Ellipsoid-Wand
    ratio = np.clip(x / params.TIP_POSITION_X, -1.0, 1.0)
    local_raumy = params.raumy * np.sqrt(1.0 - ratio**2)
    dist_radial = local_raumy - np.sqrt(y**2 + z**2) - radius
    
    # 2. Den absolut geringsten Wandabstand ermitteln
    d_wand = np.minimum.reduce([dist_apical, dist_basal, dist_radial])
    d_wand = np.maximum(0.0, d_wand)  # Schutz vor negativen Werten
    
    # 3. Effektive Viskosität berechnen
    wall_effect = 1.0 + np.exp(-d_wand / params.lambd)
    
    grenzschicht = np.where(
        d_wand < params.wall_layer_thickness,
        np.exp((params.wall_layer_thickness - d_wand) / params.wall_layer_thickness),
        1.0
    )
    
    eta_eff = params.eta_parallel * wall_effect * grenzschicht
    
    # 4. Stokes-Reibung (gamma) und Mobilität (mu) berechnen
    gamma = 6 * np.pi * eta_eff * radius
    mu = 1.0 / gamma
    
    if len(mu) == 1:
        return mu[0]
    return mu