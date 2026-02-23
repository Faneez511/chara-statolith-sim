import pyvista as pv
import numpy as np
from geometry.cell_geometry import ellipsoid_pos_x, innen, get_rhizoid_diameter
from simulation.warmup import get_initial_state
from config.parameters import N

durchmesser_rhizoid = get_rhizoid_diameter()

statolithen_data = get_initial_state(N, durchmesser_rhizoid)


p = pv.Plotter(shape="1|2", window_size=(1600, 1000), title="Statolithen Simulation")

actors_main = []
actors_xy = []
actors_xz = []

# === SUBPLOT 0: LINKS ===
arrow_mesh = pv.Arrow(start=(50, 0, 0), direction=(1, 0, 0), scale=7.0, shaft_radius=0.03, tip_length=0.1)
p.subplot(0)
p.add_text("3D Ansicht ('R' drücken für Reset)", font_size=10) 
p.add_mesh(ellipsoid_pos_x, color='r', smooth_shading=True, opacity=0.4)
p.add_mesh(innen, color='g', smooth_shading=True, opacity=0.1)
actin_plane = pv.Plane(center=(45, 0, 0), direction=(1, 0, 0), i_size=15, j_size=15)
p.add_mesh(actin_plane, color='yellow', style='wireframe', opacity=0.5)

for s in statolithen_data:
    sphere = pv.Sphere(radius=s[3], center=(0,0,0))
    actors_main.append(p.add_mesh(sphere, color='blue', smooth_shading=True))

arrow_actor = p.add_mesh(arrow_mesh, color='green')

p.show_bounds(grid='back', location='outer', ticks='both')
p.view_isometric(); p.reset_camera()   

# === SUBPLOT 1: RECHTS OBEN ===
p.subplot(1)
p.add_text("XY Ebene (Oben/Unten)", font_size=10)
p.add_mesh(ellipsoid_pos_x, color='r', style='wireframe', opacity=0.3)
p.add_mesh(innen, color='g', style='wireframe', opacity=0.3)
for s in statolithen_data:
    sphere = pv.Sphere(radius=s[3], center=(0,0,0))
    actors_xy.append(p.add_mesh(sphere, color='blue'))
arrow_actorXZ = p.add_mesh(arrow_mesh, color='green')
p.view_xy(); p.enable_parallel_projection(); p.reset_camera()    

# === SUBPLOT 2: RECHTS UNTEN ===
p.subplot(2)
p.add_text("XZ Ebene (Links/Rechts)", font_size=10)
p.add_mesh(ellipsoid_pos_x, color='r', style='wireframe', opacity=0.3)
p.add_mesh(innen, color='g', style='wireframe', opacity=0.3)
for s in statolithen_data:
    sphere = pv.Sphere(radius=s[3], center=(0,0,0))
    actors_xz.append(p.add_mesh(sphere, color='blue'))

arrow_actorXY = p.add_mesh(arrow_mesh, color='green')
p.view_xz(); p.enable_parallel_projection(); p.reset_camera()         


# --- 5. ANIMATION LOOP ---
sim_stato = np.array(statolithen_data)

dt = 0.01
TIME_SCALE = 100
current_sim_time = 0.0

# --- RESET FUNKTION ---
def reset_simulation():
    global sim_stato, current_sim_time
    print("Resetting Simulation...")
    sim_stato[:] = np.array(statolithen_data)[:] 
    current_sim_time = 0.0

p.add_key_event("r", reset_simulation)
p.add_key_event("R", reset_simulation)

p.show(interactive_update=True)