
#Zellgeometrie

LIMIT_X = 45.0                  #Begrenzung Subapkiale Zone
ACTIN_MAX_X = 45.0
TIP_POSITION_X = 50.0           #Länge der Zelle in µm
ACTIN_MIN_X = 20.0              #Begrenzung Apikale Zone
CELL_WALL = 1.5

#Kräfte/Physik

ACTIN_DECAY_LENGTH = 5.0        
ACTIN_AXIAL_FORCE = 5e-11
ACTIN_MAX_FORCE = 5e-11
ACTIN_LATERAL_FORCE = 2e-11
FORCE_DAMPING = 10.0

g_mag = 9.81 * 1e6              #Gravitationskraft
eta_parallel = 139 * 1e-6 
lambd = 5
p_cyto = 1.0139 
Kb = 1.38 * 1e-23
Temp = 293
winkel_in_XY = -90
winkel_zu_Z = 0


#Simulation

dt = 0.01
TIME_SCALE = 100
N = 50                          #Anzahl der Statolithen


