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

        for i, s in enumerate(self.state):
            self.velocities[i] += compute_forces_single(s, self.params)
            

        # NEUER SPRING-KOPPLUNGSBLOCK
        N = len(self.state)

        # In engine.py, Spring-Block ersetzen durch:
        for i in range(N):
            for j in range(i + 1, N):
                rij = self.state[j, 0:3] - self.state[i, 0:3]
                dist = np.linalg.norm(rij)
                
                if dist < 1e-10 or dist > self.params.lj_cutoff:
                    continue
                
                # Lennard-Jones: anziehed bei mittlerer Distanz, abstoßend bei Kontakt
                sig = self.params.lj_sigma  # ~1.5 µm (Partikeldurchmesser)
                eps = self.params.lj_eps    # Stärke der Anziehung

                dist_eff = max(dist, 0.8 * sig)
                
                sr6 = (sig / dist_eff) ** 6
                f_mag = 24 * eps * (2 * sr6**2 - sr6) / dist_eff
                f_mag = np.clip(f_mag, -1e-2, 1e-2)
        
                
                
                # Mobility für beide Partikel lokal berechnen
                ri = self.state[i, 3]
                rj = self.state[j, 3]
                mob_i = 1.0 / (6 * np.pi * self.params.eta_parallel * ri)
                mob_j = 1.0 / (6 * np.pi * self.params.eta_parallel * rj)
                
                f_vec = f_mag * (rij / dist)
                self.velocities[i] -= f_vec * mob_i
                self.velocities[j] += f_vec * mob_j

        for i, s in enumerate(self.state):
            r = s[3]
            pos = s[0:3]
            new_pos = pos + self.velocities[i] * dt
            new_pos += compute_brownian_motion(s, self.params)
            self.state[i][0:3] = apply_constraints(new_pos, r, self.params)

        

        self.current_time += dt

    def reset(self):
        self.state[:] = self.initial_state[:]
        self.velocities[:] = 0.0
        self.current_time = 0.0