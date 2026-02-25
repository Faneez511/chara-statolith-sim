import numpy as np
from physics.forces import compute_forces_single
from physics.brownian_motion import compute_brownian_motion
from physics.collisions import compute_collisions
from physics.constraints import apply_constraints
from visualization.plotter import initialize_plotter, update_plotter

class SimulationEngine:
    def __init__(self, sim_state, params, plotter_objects = None, ellipsoid = None, innen = None, raumy = None):
        self.initial_state = np.array(sim_state).copy()
        self.state = np.array(sim_state).copy()
        self.params = params
        self.plotter_objects = plotter_objects
        self.ellipsoid_pos_x = ellipsoid
        self.innen = innen 
        self.raumy = raumy
        self.velocities = np.zeros((len(self.state), 3))
        self.current_time = 0.0

    def step(self, dt):
        self.velocities[:] = 0.0

        for i, s in enumerate(self.state):
            self.velocities[i] += compute_forces_single(s, self.params)
            self.velocities[i] += compute_brownian_motion(s, self.params)

        v_corr = compute_collisions(self.state, self.params)
        self.velocities += v_corr

        # NEUER SPRING-KOPPLUNGSBLOCK
        N = len(self.state)

        for i in range(N):
            for j in range(i + 1, N):

                rij = self.state[j, 0:3] - self.state[i, 0:3]
                dist = np.linalg.norm(rij)

                if dist == 0:
                    continue  # Sicherheitscheck gegen Division durch 0

                if dist < self.params.spring_cutoff:

                    spring_dir = rij / dist
                    spring_force = -self.params.spring_k * (dist - self.params.spring_rest)

                    self.velocities[i] += spring_force * spring_dir
                    self.velocities[j] -= spring_force * spring_dir

        for i, s in enumerate(self.state):
            r = s[3]
            pos = s[0:3]
            new_pos = pos + self.velocities[i] * dt
            self.state[i][0:3] = apply_constraints(new_pos, r, self.params)

        if self.plotter_objects is not None:
            update_plotter(self.state, self.plotter_objects)

        self.current_time += dt

    def reset(self):
        self.state[:] = self.initial_state[:]
        self.velocities[:] = 0.0
        self.current_time = 0.0

        if self.plotter_objects is not None:
            update_plotter(self.state, self.plotter_objects)