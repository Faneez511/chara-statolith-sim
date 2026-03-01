# visualization/plotter.py
import pyvista as pv
import numpy as np

def initialize_plotter(sim_state, ellipsoid_pos_x, innen):
    p = pv.Plotter(shape="1|2", window_size=(1600, 1000), title="Statolithen Simulation")

    actors_main = []
    actors_xy = []
    actors_xz = []

    # --- SUBPLOT 0 ---
    p.subplot(0)
    p.add_text("3D Ansicht ('R' drücken für Reset)", font_size=10) 
    p.add_mesh(ellipsoid_pos_x, color='r', smooth_shading=True, opacity=0.4)
    p.add_mesh(innen, color='g', smooth_shading=True, opacity=0.1)
    actin_plane = pv.Plane(center=(45, 0, 0), direction=(1, 0, 0), i_size=15, j_size=15)
    p.add_mesh(actin_plane, color='yellow', style='wireframe', opacity=0.5)

    for s in sim_state:
        sphere = pv.Sphere(radius=s[3], center=(0,0,0))
        actors_main.append(p.add_mesh(sphere, color='blue', smooth_shading=True))

    p.show_bounds(grid='back', location='outer', ticks='both')  
    p.view_isometric(); p.reset_camera()

    # --- SUBPLOT 1 ---
    p.subplot(1)
    p.add_text("XY Ebene (Oben/Unten)", font_size=10)
    p.add_mesh(ellipsoid_pos_x, color='r', style='wireframe', opacity=0.3)
    p.add_mesh(innen, color='g', style='wireframe', opacity=0.3)
    for s in sim_state:
        sphere = pv.Sphere(radius=s[3], center=(0,0,0))
        actors_xy.append(p.add_mesh(sphere, color='blue'))
    p.view_xy(); p.enable_parallel_projection(); p.reset_camera()  

    # --- SUBPLOT 2 ---
    p.subplot(2)
    p.add_text("XZ Ebene (Links/Rechts)", font_size=10)
    p.add_mesh(ellipsoid_pos_x, color='r', style='wireframe', opacity=0.3)
    p.add_mesh(innen, color='g', style='wireframe', opacity=0.3)
    for s in sim_state:
        sphere = pv.Sphere(radius=s[3], center=(0,0,0))
        actors_xz.append(p.add_mesh(sphere, color='blue'))
    p.view_xz(); p.enable_parallel_projection(); p.reset_camera()  

    # --- RESET FUNKTION ---
    current_sim_time = [0.0]  # Liste, damit mutable
    def reset_simulation():
        
        nonlocal current_sim_time
        for i, s in enumerate(sim_state):
            # Reset Positionen
            actors_main[i].SetPosition(s[0:3])
            actors_xy[i].SetPosition(s[0:3])
            actors_xz[i].SetPosition(s[0:3])
        current_sim_time[0] = 0.0
        print("Simulation reset!")


    p.show(interactive_update=True)

    return {
        "plotter": p,
        "actors_main": actors_main,
        "actors_xy": actors_xy,
        "actors_xz": actors_xz,
        "current_sim_time": current_sim_time
    }

def update_plotter(sim_state, plotter_objects):
    """
    Aktualisiert die Position der Statolithen-Spheres im Plotter.
    plotter_objects kann ein dict mit:
        'actors_main', 'actors_xy', 'actors_xz'
    """
    actors_main = plotter_objects['actors_main']
    actors_xy = plotter_objects['actors_xy']
    actors_xz = plotter_objects['actors_xz']

    for i, s in enumerate(sim_state):
        pos = s[0:3]
        actors_main[i].SetPosition(pos)
        actors_xy[i].SetPosition(pos)
        actors_xz[i].SetPosition(pos)


