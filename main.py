from simulation.engine import SimulationEngine
from simulation.warmup import get_initial_state
from config.parameters import Parameters
from visualization.plotter import initialize_plotter

params = Parameters()
sim_state = get_initial_state(params.N, params.d_rhizoid)
plotter_objects = initialize_plotter(sim_state, params)

engine = SimulationEngine(sim_state, params, plotter_objects)

dt = 0.01
for step in range(1000):
    engine.step(dt)