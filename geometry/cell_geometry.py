import pyvista as pv
from ui.input_dialog import get_rhizoid_diameter
from config.parameters import CELL_WALL

durchmesser_rhizoid = get_rhizoid_diameter()

mittelpunkt = durchmesser_rhizoid / 2
raumy = mittelpunkt - CELL_WALL

mesh = pv.ParametricEllipsoid(xradius=50, yradius=mittelpunkt, zradius=mittelpunkt)
ellipsoid_pos_x = mesh.clip(normal=(-1,0,0), origin=(0,0,0))
