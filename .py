import numpy as np
import cv2

import torch

from filament import Filament

'''
MARK: KEY PRINCIPLE

            |             |             |                |             |
       E_f0 |        E_f1 |        E_f2 |                |    E_f(n-1) |        E_fn
----------> | ----------> | ----------> | ----......---> | ----------> | ---------->
            |             |             |                |             |
<---------- | <---------- | <---------- | <---......---- | <---------- | <----------
E_b0        | E_b1        | E_b2        |                | E_b(n-1)    | E_bn
            |             |             |                |             |

            
E : the expectation of the number of passing for one photon

E_f0, E_bn given
E_b0, E_fn needed (exactly the same as the ratio of the intensity)


modelled by Markov chain, we get: 

E_fi = P[i-1][i] * E_f(i-1) + R[i][i-1] * E_bi
E_bi = P[i+1][i] * E_b(i+1) + R[i][i+1] * E_fi

for each i


where: 

r[i][j] = ( (n_i - n_j) / (n_i + n_j) ) ** 2  # reflected ratio at the surface
P[i][j] = (1 - r[i][j]) * exp(-K[j] * d)
R[i][j] = r[i][j] * exp(-K[i] * d)


get E_b0 and E_fn by solving the simultaneous equations

'''

class Pyforge:

    AIR = Filament("Nature", 'Air')
    AIR.extinction_coefficient = np.array(0, 0, 0)
    AIR.refractive_index = np.array(1, 1, 1)
    # considered as no intensity diminishing

    def __init__(self, available_filaments, thickness, picture):

        self.all_fila = available_filaments + [Pyforge.AIR]
        self.thickness = thickness
        self.picture = picture

        self.num_fila = len(self.all_fila)

        self.P = np.zeros((self.num_fila, self.num_fila))
        self.R = np.zeros((self.num_fila, self.num_fila))
        # the meaning has been shown in KEY PRINCIPLE

        for i in range(self.num_fila):
            for j in range(self.num_fila):
                reflectance = Filament.SurfReflct(self.all_fila[i], self.all_fila[j])

                self.P[i][j] = (1 - reflectance) * Filament.LambertEffct(self.all_fila[j], self.thickness)
                # the light passes through fila j

                self.R[i][j] = reflectance * Filament.LambertEffct(self.all_fila[i], self.thickness)
                # the light passes through fila i

'''
MARK : WHEN SOLVING THE SIMULTANEOUS EQUATIONS

as deleting a row or a col in tensor is a relatively slow operation, 
use dynamic indexing in the matrix to speed up

use a double-directed linked list to store layers of filaments
(need to write in C++ as python's list is too slow)
(use an extra linked list to store empty nodes to save space (? no python library achieves this) )

ensure the first 4 rows / cols are inputs / outputs

just need to modify several items in the matrix / concate noew row and col
O(1)

the permutation of the rest does not matters

'''


'''

OTHER NOTES

- use jit and for statement to speed up the SA loop
- the distance (kind of loss func) should emphasize the difference in brightness
- a maximum number of layers should be set as things get crazy near (0, 0, 0)
    - maybe a minimum as well

'''