import pyvista as pv
from ui.input_dialog import get_rhizoid_diameter
from config.parameters import CELL_WALL

durchmesser_rhizoid = get_rhizoid_diameter()
if durchmesser_rhizoid is None:
    durchmesser_rhizoid = 15.0

mittelpunkt = durchmesser_rhizoid / 2.0
raumy = mittelpunkt - CELL_WALL

mesh = pv.ParametricEllipsoid(xradius=50, yradius=mittelpunkt, zradius=mittelpunkt)
ellipsoid_pos_x = mesh.clip(normal=(-1,0,0), origin=(0,0,0))

mesh2 = pv.ParametricEllipsoid(xradius=50, yradius=raumy, zradius=raumy)
innen = mesh2.clip(normal=(-1,0,0), origin=(0,0,0))