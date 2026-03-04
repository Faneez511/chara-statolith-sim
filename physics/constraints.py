import numpy as np

def apply_constraints(pos, r, params):
    new_pos = pos.copy()
    
    # 1. Zylinder-Check
    y, z = float(new_pos[1]), float(new_pos[2])
    r_current = np.sqrt(y**2 + z**2)
    r_max_allowed = params.raumy - r
    if r_current > r_max_allowed and r_current > 0:
        scale_factor = r_max_allowed / r_current
        new_pos[1] *= scale_factor
        new_pos[2] *= scale_factor
    
    # 2. Ellipsoid-Kappe (Erster Pass)
    limit_x_eff = float(params.LIMIT_X - r)
    limit_yz_eff = float(params.raumy - r)
    if limit_x_eff > 0 and limit_yz_eff > 0:
        val_test = (new_pos[0]/limit_x_eff)**2 + (new_pos[1]/limit_yz_eff)**2 + (new_pos[2]/limit_yz_eff)**2
        if val_test > 1.0:
            norm_factor = np.sqrt(val_test)
            new_pos[0] /= norm_factor
            new_pos[1] /= norm_factor
            new_pos[2] /= norm_factor

    # 3. Harte X-Limits
    if new_pos[0] < params.ACTIN_MIN_X + r:
        new_pos[0] = params.ACTIN_MIN_X + r
    elif new_pos[0] > params.LIMIT_X - r:
        new_pos[0] = params.LIMIT_X - r

    # 4. Zweiter Ellipsoid-Check (Sicherheitsnetz für den Restfall aus Review v3) 
    # Falls Schritt 3 (X-Limits) das Partikel nach vorne geschoben hat, prüfen wir hier erneut.
    if limit_x_eff > 0 and limit_yz_eff > 0:
        val2 = (new_pos[0]/limit_x_eff)**2 + (new_pos[1]/limit_yz_eff)**2 + (new_pos[2]/limit_yz_eff)**2
        if val2 > 1.0:
            nf2 = np.sqrt(val2)
            new_pos[0] /= nf2
            new_pos[1] /= nf2
            new_pos[2] /= nf2
            
    return new_pos