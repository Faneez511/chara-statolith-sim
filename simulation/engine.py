import numpy as np
from physics.forces import compute_forces_single
from physics.brownian_motion import compute_brownian_motion
from physics.constraints import apply_constraints


class SimulationEngine:
    def __init__(self, sim_state, params):
        self.initial_state = np.array(sim_state).copy()
        self.state = np.array(sim_state).copy()
        self.params = params
        self.velocities = np.zeros((len(self.state), 3))
        self.current_time = 0.0

    def step(self, dt):
        self.velocities[:] = 0.0

        # --- 1. Deterministische Kräfte (Gravitation, Aktin) ---
        for i, s in enumerate(self.state):
            self.velocities[i] += compute_forces_single(s, self.params)
            
        pos = self.state[:, 0:3]
        radii = self.state[:, 3]

        # --- 2. Wand-Effekt (Mobilität) vektorisiert ---
        pos_x = pos[:, 0]
        pos_y = pos[:, 1]
        pos_z = pos[:, 2]

        dist_x = self.params.LIMIT_X - pos_x
        x_safe = np.clip(pos_x, 0.0, self.params.TIP_POSITION_X)
        local_raumy_arr = self.params.raumy * np.sqrt(1.0 - (x_safe / self.params.TIP_POSITION_X)**2)
        dist_radial = local_raumy_arr - np.sqrt(pos_y**2 + pos_z**2)
        d_wand = np.maximum(np.minimum(dist_x, dist_radial), 0.0)
        
        wall_effect = (1.0 - self.params.wall_mobility_factor) * np.exp(-d_wand / (self.params.wall_layer_thickness / 3.0))
        eta_eff_arr = self.params.eta_parallel * (1.0 + np.exp(-d_wand / (self.params.lambd)))
        mobilities = (1.0 / (6 * np.pi * eta_eff_arr * radii)) * (1.0 - wall_effect)        

        # --- 3. Lennard-Jones Interaktion vektorisiert ---
        # Matrix aller Distanzvektoren (i nach j)
        pos_j = pos[np.newaxis, :, :]
        pos_i = pos[:, np.newaxis, :]
        rij = pos_j - pos_i
        
        # Matrix der skalaren Distanzen
        dist = np.linalg.norm(rij, axis=2)

        # Maske für Interaktionen innerhalb des Cutoffs (ignoriert i=j)
        mask = (dist > 1e-10) & (dist <= self.params.lj_cutoff)

        # Division durch 0 absichern
        dist_safe = np.where(mask, dist, 1.0)
        dist_eff = np.maximum(dist_safe, 0.8 * self.params.lj_sigma)
        
        sig = self.params.lj_sigma
        eps = self.params.lj_eps
        
        # LJ-Kraftbetrag
        sr6 = (sig / dist_eff) ** 6
        f_mag = 24 * eps * (2 * sr6**2 - sr6) / dist_eff
        f_mag = np.clip(f_mag, -1e-2, 1e-2)

        # Vektorielle Kräfte berechnen
        f_vec = np.zeros_like(rij)
        f_vec[mask] = f_mag[mask, np.newaxis] * (rij[mask] / dist_safe[mask, np.newaxis])

        # Summe der Kräfte auf Partikel i (Kraft zeigt weg von j, daher -f_vec)
        total_lj_force_on_i = -np.sum(f_vec, axis=1)

        # Geschwindigkeiten updaten (Kraft * individuelle Mobilität)
        self.velocities += total_lj_force_on_i * mobilities[:, np.newaxis]

        # --- 4. Velocity Clipping vektorisiert ---
        v_mag = np.linalg.norm(self.velocities, axis=1)
        step_dist = v_mag * dt
        
        clip_mask = step_dist > self.params.MAX_STEP
        scale = np.where(clip_mask, self.params.MAX_STEP / step_dist, 1.0)
        self.velocities *= scale[:, np.newaxis]

        # --- 5. Euler-Maruyama Integration & Constraints ---
        for i, s in enumerate(self.state):
            r = s[3]
            current_pos = s[0:3]
            new_pos = current_pos + self.velocities[i] * dt
            new_pos += compute_brownian_motion(s, self.params, dt)
            self.state[i][0:3] = apply_constraints(new_pos, r, self.params)

        self.current_time += dt

    def get_current_velocities(self):
        return np.mean(self.velocities, axis=0)

    def get_contact_count(self):
        pos = self.state[:, 0:3]
        dist = np.linalg.norm(pos[np.newaxis, :, :] - pos[:, np.newaxis, :], axis=2)
        mask = (dist > 1e-10) & (dist < 1.1 * self.params.lj_sigma)
        return np.sum(mask) // 2

    def reset(self):
        self.state[:] = self.initial_state[:]
        self.velocities[:] = 0.0
        self.current_time = 0.0