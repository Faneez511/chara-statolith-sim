from ui.input_dialog import get_rhizoid_diameter
from geometry.cell_geometry import get_cell_meshes
from simulation.warmup import get_initial_state
from config.parameters import Parameters
from visualization.plotter import initialize_plotter
from simulation.engine import SimulationEngine
import pyvista as pv
from visualization.plotter import initialize_plotter, update_plotter

# 1. Rhizoid-Durchmesser abfragen
durchmesser_rhizoid = get_rhizoid_diameter()
if durchmesser_rhizoid is None:
    durchmesser_rhizoid = 15.0

# 2. Zellgeometrie erzeugen
ellipsoid_pos_x, innen, raumy, mittelpunkt = get_cell_meshes(durchmesser_rhizoid)

# 3. Parameter & Initialzustand
params = Parameters()
sim_state = get_initial_state(params.N, durchmesser_rhizoid, raumy, params)

params.raumy = mittelpunkt - params.CELL_WALL

# 4. Plotter initialisieren
plotter_objects = initialize_plotter(sim_state, ellipsoid_pos_x, innen)

# 5. Engine erstellen
engine = SimulationEngine(sim_state, params, plotter_objects, ellipsoid_pos_x, innen, raumy)

# 6. Simulation starten
# --- nach allen Plot-Setup-Schritten ---
# 6. Simulation starten
dt = 0.01
# 4. Plotter initialisieren
plotter_objects = initialize_plotter(sim_state, ellipsoid_pos_x, innen)
p = plotter_objects['plotter']  # <- Hier benutzen wir genau diesen Plotter

# Interaktives Fenster starten – nur einmal!
p.show(interactive_update=True)

# --- Simulation Schleife ---
while True:
    engine.step(dt)  # berechnet neue Positionen etc.
    
    # Positionen der Meshes updaten
    update_plotter(engine.state, plotter_objects)
    
    # Anzeige aktualisieren
    p.update()
    
    # Fenster geschlossen → beenden
    if hasattr(p, 'closed') and p.closed:
        print("Plotter geschlossen – Simulation beendet")
        break
    
    