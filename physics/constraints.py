import numpy as np

def apply_constraints(pos, r, params):
    new_pos = pos.copy()
    
    # 1. Zylinder-Check (Lateral Y/Z) - Bleibt als Basis bestehen
    y, z = float(new_pos[1]), float(new_pos[2])
    r_current = np.sqrt(y**2 + z**2)
    r_max_allowed = params.raumy - r
    if r_current > r_max_allowed and r_current > 0:
        scale_factor = r_max_allowed / r_current
        new_pos[1] *= scale_factor
        new_pos[2] *= scale_factor
    
    # 2. Ellipsoid-Kappe (Zuerst normieren)
    # Wenn das Teilchen hier skaliert wird, ändern sich X, Y und Z proportional
    limit_x_eff = float(params.LIMIT_X - r)
    limit_yz_eff = float(params.raumy - r)
    if limit_x_eff > 0 and limit_yz_eff > 0:
        val_test = (new_pos[0]/limit_x_eff)**2 + (new_pos[1]/limit_yz_eff)**2 + (new_pos[2]/limit_yz_eff)**2
        if val_test > 1.0:
            norm_factor = np.sqrt(val_test)
            new_pos[0] /= norm_factor
            new_pos[1] /= norm_factor
            new_pos[2] /= norm_factor

    # 3. Harte X-Limits (Als finaler Sicherheits-Check am Ende)
    # Dies korrigiert den Fehler, dass X durch die Normierung zu klein wurde
    if new_pos[0] < params.ACTIN_MIN_X + r:
        new_pos[0] = params.ACTIN_MIN_X + r
    elif new_pos[0] > params.LIMIT_X - r:
        new_pos[0] = params.LIMIT_X - r
    
    return new_pos