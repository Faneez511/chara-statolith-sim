# main.py
import os
print(f"Aktuelles Arbeitsverzeichnis: {os.getcwd()}")

from ui.input_dialog import get_rhizoid_diameter
from geometry.cell_geometry import get_cell_meshes
from simulation.warmup import get_initial_state
from config.parameters import Parameters
from visualization.plotter import initialize_plotter, update_plotter
from simulation.engine import SimulationEngine
import pyvista as pv
import numpy as np

# --- 1. Rhizoid-Durchmesser abfragen ---
durchmesser_rhizoid = get_rhizoid_diameter()
if durchmesser_rhizoid is None:
    durchmesser_rhizoid = 15.0

print(f"Simulation gestartet mit Rhizoid-Durchmesser: {durchmesser_rhizoid} µm")

# --- 2. Zellgeometrie erzeugen ---
ellipsoid_pos_x, innen, raumy, mittelpunkt = get_cell_meshes(durchmesser_rhizoid)

# --- 3. Parameter & Initialzustand ---
params = Parameters()
params.raumy = mittelpunkt - params.CELL_WALL

# ruft neue get_initial_state Version auf, berücksichtigt jetzt N, Durchmesser, raumy und params
sim_state = np.array(get_initial_state(params.N, durchmesser_rhizoid, raumy, params))

# --- 4. Plotter initialisieren ---
plotter_objects = initialize_plotter(sim_state, ellipsoid_pos_x, innen)
p = plotter_objects['plotter']  # Referenz auf den Plotter

# --- 5. Simulation Engine erstellen ---
engine = SimulationEngine(sim_state, params, plotter_objects, ellipsoid_pos_x, innen, raumy)

dt = 0.01

# --- 6. Simulation Schleife ---
while True:
    engine.step(dt)  # Berechnet neue Positionen
    
    # Positionen der Meshes aktualisieren
    update_plotter(engine.state, plotter_objects)
    
    # Anzeige aktualisieren
    p.update()
    
    # Beenden, wenn Fenster geschlossen
    if hasattr(p, 'closed') and p.closed:
        print("Plotter geschlossen – Simulation beendet")
        break