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
engine = SimulationEngine(sim_state, params)


# --- 6. Simulation Schleife ---
sim_time = [0.0]  # simulierte Zeit
display_interval = 0.5  # alle 0.5 s GUI-Update für Zeit
accum_time = [0.0]

# Textobjekt für Timer in der Szene erstellen

time_text = p.add_text(f"Simulierte Zeit: 0.00 s", position='lower_right', font_size=14)

# --- Reset-Funktion ---
def reset_simulation():
    engine.reset()       # Engine zurücksetzen auf Anfangszustand
    sim_time[0] = 0.0
    accum_time[0] = 0.0
    print("Simulation zurückgesetzt!")
    

p.add_key_event("r", reset_simulation)
p.add_key_event("R", reset_simulation)

while True:
    engine.step(params.dt)       # Berechnet neue Positionen
    sim_time[0] += params.dt
    accum_time[0] += params.dt

    # Positionen der Meshes aktualisieren
    update_plotter(engine.state, plotter_objects)

    # Timer nur alle display_interval aktualisieren
    if accum_time[0] >= display_interval:
        corner = 1  # obere linke Ecke
        time_text.SetText(corner, f"Simulierte Zeit: {sim_time[0]:.2f} s")
        
        accum_time[0] = 0.0

    

    p.update()

    # Beenden, wenn Fenster geschlossen
    if hasattr(p, 'closed') and p.closed:
        print(f"Simulation beendet bei simulierten {sim_time[0]:.2f} s")
        break