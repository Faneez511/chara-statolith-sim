

class Parameters:
    def __init__(self):

        #Zellgeometrie

        self.LIMIT_X = 45.0                  #Begrenzung Subapkiale Zone
        self.ACTIN_MAX_X = 45.0
        self.TIP_POSITION_X = 50.0           #Länge der Zelle in µm
        self.ACTIN_MIN_X = 20.0              #Begrenzung Apikale Zone
        self.CELL_WALL = 1.5

        #Kräfte/Physik

        self.ACTIN_DECAY_LENGTH = 5.0        
        self.ACTIN_AXIAL_FORCE = 5e-11
        self.ACTIN_MAX_FORCE = 2.0e-4
        self.ACTIN_LATERAL_FORCE = 0.5e-4
        

        self.g_mag = 9.81e6              #Gravitationskraft
        self.eta_parallel = 139e-6
        self.lambd = 5
        self.p_cyto = 1.0139 
        self.Kb = 1.38e-23 * 1e15
        self.Temp = 293
        self.winkel_in_XY = -45
        self.winkel_zu_Z = 0

        # Spring network (Actin coupling)
        
        self.lj_sigma = 1.3    # µm
        self.lj_eps = 5e-5     # schwach anziehend
        self.lj_cutoff = 5.0   # µm
                


        self.wall_layer_thickness = 2.0      # z.B. 2 µm
        self.wall_mobility_factor = 0.2       # 80% Reduktion


        #Simulation

        self.dt = 0.05
        self.TIME_SCALE = 100
        self.N = 50                          #Anzahl der Statolithen


