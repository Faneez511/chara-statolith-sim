

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
        self.ACTIN_MAX_FORCE = 5e-11
        self.ACTIN_LATERAL_FORCE = 2e-11
        self.FORCE_DAMPING = 10.0

        self.g_mag = 9.81e6              #Gravitationskraft
        self.eta_parallel = 139 * 1e-6 
        self.lambd = 5
        self.p_cyto = 1.0139 
        self.Kb = 1.38 * 1e-23
        self.Temp = 293
        self.winkel_in_XY = -45
        self.winkel_zu_Z = 0

        # Spring network (Actin coupling)
        
        self.spring_k = 1e-4
        self.spring_rest = 1.0       # µm – Gleichgewichtsabstand (≈ Partikeldurchmesser)
        self.spring_cutoff = 5.0      # µm – maximale Kopplungsreichweite
        


        #Simulation

        self.dt = 0.01
        self.TIME_SCALE = 100
        self.N = 50                          #Anzahl der Statolithen


