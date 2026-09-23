import numpy as np
from physics.hydrodynamics import get_local_mobility

def compute_brownian_motion(pos, radius, params):
    """
    Berechnet die thermische Verschiebung eines Partikels
    streng nach dem Fluktuations-Dissipations-Theorem.
    """
    # 1. Korrekte lokale Mobilität abrufen
    mu = get_local_mobility(pos, radius, params)
    
    # 2. Diffusionskoeffizient aus der Einstein-Relation berechnen
    D = params.Kb * params.Temp * mu
    
    # 3. Standardabweichung für das Wiener-Inkrement (Euler-Maruyama)
    std_dev = np.sqrt(2 * D * params.dt)
    
    # 4. Zufällige Verschiebung (Rauschen)
    displacement = np.random.normal(0.0, std_dev, 3)
    
    return displacement