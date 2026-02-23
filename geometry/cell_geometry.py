def get_cell_meshes(durchmesser_rhizoid):
    import pyvista as pv
    from config.parameters import Parameters

    param = Parameters()
    

    mittelpunkt = durchmesser_rhizoid / 2.0
    raumy = mittelpunkt - param.CELL_WALL

    mesh = pv.ParametricEllipsoid(xradius=50, yradius=mittelpunkt, zradius=mittelpunkt)
    ellipsoid_pos_x = mesh.clip(normal=(-1,0,0), origin=(0,0,0))

    mesh2 = pv.ParametricEllipsoid(xradius=50, yradius=raumy, zradius=raumy)
    innen = mesh2.clip(normal=(-1,0,0), origin=(0,0,0))

    return ellipsoid_pos_x, innen, raumy, mittelpunkt