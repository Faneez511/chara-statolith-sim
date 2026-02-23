import numpy as np

def compute_collisions(states, params):
    """
    Berechnet repulsive Geschwindigkeitskorrekturen
    für überlappende Statolithen.

    states: ndarray (N,5) -> [x,y,z,r,density]
    """

    N = len(states)
    v_corr = np.zeros((N, 3))

    for i in range(N):
        for j in range(i + 1, N):

            rij = states[i, 0:3] - states[j, 0:3]
            dist = np.linalg.norm(rij)
            rad_sum = states[i, 3] + states[j, 3]

            if dist < rad_sum and dist > 1e-12:
                overlap = rad_sum - dist
                n_vec = rij / dist

                # lineare Repulsion
                repulsion = n_vec * overlap * params.FORCE_DAMPING

                v_corr[i] += repulsion
                v_corr[j] -= repulsion

    return v_corr