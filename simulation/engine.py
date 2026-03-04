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
            

        N = len(self.state)

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

        # Verhindert Explosionen bei harten Kollisionen
        for i in range(len(self.velocities)):
            v = self.velocities[i]
            # Betrag der Geschwindigkeit berechnen
            v_mag = np.linalg.norm(v)
            
            # Wie weit würde es fliegen?
            dist = v_mag * dt
            
            if dist > self.params.MAX_STEP:
                # Skalierungsfaktor berechnen + "bremsen"
                scale = self.params.MAX_STEP / dist
                self.velocities[i] *= scale


        for i, s in enumerate(self.state):
            r = s[3]
            pos = s[0:3]
            new_pos = pos + self.velocities[i] * dt
            new_pos += compute_brownian_motion(s, self.params)
            self.state[i][0:3] = apply_constraints(new_pos, r, self.params)

        

        self.current_time += dt

    # In SimulationEngine Klasse (engine.py)

    def get_current_velocities(self):
        # Gibt den Mittelwert der aktuellen Geschwindigkeitsvektoren zurück
        return np.mean(self.velocities, axis=0)

    def get_contact_count(self):
        # Zählt, wie viele Partikel-Paare sich berühren (Abstand < 1.1 * Durchmesser)
        count = 0
        N = len(self.state)
        threshold = 1.1 * self.params.lj_sigma
        for i in range(N):
            for j in range(i + 1, N):
                dist = np.linalg.norm(self.state[i, 0:3] - self.state[j, 0:3])
                if dist < threshold:
                    count += 1
        return count


    def reset(self):
        self.state[:] = self.initial_state[:]
        self.velocities[:] = 0.0
        self.current_time = 0.0