import numpy as np

def apply_constraints(pos, r, params):
    """
    Wendet harte Constraints auf die Position eines Partikels an.
    
    pos : np.array, aktuelle Position [x, y, z]
    r : float, Radius des Partikels
    params : Objekt mit Zellparametern (LIMIT_X, raumy, ACTIN_MIN_X, ACTIN_MAX_X)
    
    Rückgabe: neue, korrigierte Position
    """
    new_pos = pos.copy()
    
    # 1. Zylinder-Check (Lateral Y/Z)
    r_current = np.sqrt(new_pos[1]**2 + new_pos[2]**2)
    r_max_allowed = params.raumy - r
    if r_current > r_max_allowed:
        scale_factor = r_max_allowed / r_current
        new_pos[1] *= scale_factor
        new_pos[2] *= scale_factor
    
    # 2. X-Limits (Vorne/Hinten)
    if new_pos[0] < params.ACTIN_MIN_X + r:
        new_pos[0] = params.ACTIN_MIN_X + r
    elif new_pos[0] > params.LIMIT_X - r:
        new_pos[0] = params.LIMIT_X - r
    
    # 3. Ellipsoid-Kappe (Approximation für die Spitze)
    limit_x_eff = params.LIMIT_X - r
    limit_yz_eff = params.raumy - r
    if limit_x_eff > 0 and limit_yz_eff > 0:
        val_test = (new_pos[0]/limit_x_eff)**2 + (new_pos[1]/limit_yz_eff)**2 + (new_pos[2]/limit_yz_eff)**2
        if val_test > 1.0:
            new_pos /= np.sqrt(val_test)
    
    return new_pos