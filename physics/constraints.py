import numpy as np

def apply_constraints(pos, r, params):
    new_pos = pos.copy()
    
    # --- 1. Harte X-Limits (Längsachse) ---
    # Partikel darf nicht hinter die basale Aktin-Wand oder über die absolute Spitze hinaus
    x_min = params.ACTIN_MIN_X + r
    x_max = params.TIP_POSITION_X - r 
    
    if new_pos[0] < x_min:
        new_pos[0] = x_min
    elif new_pos[0] > x_max:
        new_pos[0] = x_max
        
    # --- 2. Lokale Ellipsoid-Grenze für Y und Z ---
    # Wir nutzen exakt dieselbe Ellipsoid-Gleichung wie in forces.py
    x_safe = new_pos[0]
    local_raumy = params.raumy * np.sqrt(1.0 - (x_safe / params.TIP_POSITION_X)**2)
    r_max_allowed = local_raumy - r
    
    # --- 3. Radialer Check (Nur Y und Z korrigieren!) ---
    if r_max_allowed <= 0:
        # Partikel ist ganz vorne in der verengten Spitze -> exakt auf der Mittelachse zentrieren
        new_pos[1] = 0.0
        new_pos[2] = 0.0
    else:
        y, z = new_pos[1], new_pos[2]
        r_current = np.sqrt(y**2 + z**2)
        
        # Falls das Partikel außerhalb der lokalen Ellipsoid-Schale ist,
        # schieben wir es radial exakt an die Wand zurück.
        # WICHTIG: new_pos[0] (X) wird hier NICHT mehr angetastet!
        if r_current > r_max_allowed:
            scale_factor = r_max_allowed / r_current
            new_pos[1] *= scale_factor
            new_pos[2] *= scale_factor
            
    return new_pos