
def euler_maruyama_step(states, v_det, v_coll, v_brown, params):
    """
    Führt einen Integrationsschritt durch.
    
    states  : ndarray (N,5)
    v_det   : deterministische Geschwindigkeiten
    v_coll  : Kollisionskorrekturen
    v_brown : Brownsche Positionsinkremente
    """

    # deterministische Anteile
    states[:, 0:3] += v_det * params.dt
    
    # Kollisionen
    states[:, 0:3] += v_coll * params.dt
    
    # Brownsche Bewegung (bereits sqrt(2D dt))
    states[:, 0:3] += v_brown