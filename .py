import numpy as np
import cv2

import torch
import pcbridge

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
    AIR.extinction_coefficient = np.array([0, 0, 0])
    AIR.refractive_index = np.array([1, 1, 1])
    # considered as no intensity diminishing

    def _init_matrix(self):
        '''
        INITIALIZE THE MATRIX: 

        the outside 2 air layers should be put at the first 4 rows / cols
        '''

        self.matrix = torch.zeros((self.max_layer * 2, self.max_layer * 2), dtype = torch.float32, device = self.gpu)

        # E_f0
        self.matrix[0][0] = torch.tensor([-1, -1, -1])

        # E_b0
        self.matrix[1][0] = self.R[-1][-1]
        self.matrix[1][1] = torch.tensor([-1, -1, -1])
        self.matrix[1][3] = self.P[-1][-1]

        # E_fn
        self.matrix[2][0] = self.P[-1][-1]
        self.matrix[2][2] = torch.tensor([-1, -1, -1])
        self.matrix[2][3] = self.R[-1][-1]

        # E_bn
        self.matrix[3][3] = torch.tensor([-1, -1, -1])

        for i in range(self.max_layer * 2):
            self.matrix[i][i] = torch.tensor([-1, -1, -1])

    def __init__(self, available_filaments, thickness, max_layer = 40, gpu = 'mps'):
        
        self.gpu = gpu
        self.max_layer = max_layer

        self.all_fila = available_filaments + [Pyforge.AIR]
        self.thickness = thickness

        self.num_fila = len(self.all_fila)
        
        # linked list storing the current layer order via C++ extension
        self.layer_list = pcbridge.DoublyList()
        # initialize with the two boundary air layers (index = num_fila - 1)
        self.layer_list.append(self.num_fila - 1)  # left air
        self.layer_list.append(self.num_fila - 1)  # right air

        self.P = torch.zeros((self.num_fila, self.num_fila, 3))
        self.R = torch.zeros((self.num_fila, self.num_fila, 3))
        # the meaning has been shown in KEY PRINCIPLE

        for i in range(self.num_fila):
            for j in range(self.num_fila):
                reflectance = Filament.SurfReflct(self.all_fila[i], self.all_fila[j])

                self.P[i][j] = torch.from_numpy( (1 - reflectance) * Filament.LambertEffct(self.all_fila[j], self.thickness))
                # the light passes through fila j

                self.R[i][j] = torch.from_numpy( reflectance * Filament.LambertEffct(self.all_fila[i], self.thickness))
                # the light passes through fila i
        

    # THINGS NEEDED FOR SOLVING THE SIMULTANEOUS EQUATIONS

        self.outcome = torch.zeros((2 * self.max_layer, 3))
        # the vector at the right of the simultaneous equations

        self.matrix = torch.zeros((self.max_layer * 2, self.max_layer * 2), dtype = torch.float32, device = self.gpu)
        # the matrix of the simultaneous equations

        self._init_matrix()

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

    def _modifyMatrixAdd(self, id, pre_id, nxt_id, fila, pre_fila, nxt_fila):
        '''
        the id(s) here are (kind of ?) the index of the matrix
            (actually E_fi is in (2*id) and E_bi is in (2*id + 1) )
        the fila(s) here are the index of the filament 
            (that used for P and R)
        '''

        fid = 2 * id
        bid = 2 * id + 1

        pre_fid = 2 * pre_id
        pre_bid = 2 * pre_id + 1

        nxt_fid = 2 * nxt_id
        nxt_bid = 2 * nxt_id + 1

        # E_fi = P[i-1][i] * E_f(i-1) + R[i][i-1] * E_bi
        # E_bi = P[i+1][i] * E_b(i+1) + R[i][i+1] * E_fi

        self.matrix[pre_bid][nxt_bid] = torch.tensor([0, 0, 0])
        self.matrix[pre_bid][bid] = self.P[fila][pre_fila]

        self.matrix[nxt_fid][pre_fid] = torch.tensor([0, 0, 0])
        self.matrix[nxt_fid][fid] = self.P[fila][nxt_fila]

        self.matrix[fid][pre_fid] = self.P[pre_fila][fila]
        self.matrix[fid][bid] = self.R[pre_fila][fila]

        self.matrix[bid][nxt_bid] = self.P[nxt_fila][fila]
        self.matrix[bid][fid] = self.R[nxt_fila][fila]
    
    def _modifyMatrixRpl(self, id, pre_id, nxt_id, fila, pre_fila, nxt_fila):
        '''
        the id(s) here are (kind of ?) the index of the matrix
            (actually E_fi is in (2*id) and E_bi is in (2*id + 1) )
        the fila(s) here are the index of the filament 
            (that used for P and R)
            (fila here is the index of the new filament)
        '''

        fid = 2 * id
        bid = 2 * id + 1

        pre_fid = 2 * pre_id
        pre_bid = 2 * pre_id + 1

        nxt_fid = 2 * nxt_id
        nxt_bid = 2 * nxt_id + 1

        # E_fi = P[i-1][i] * E_f(i-1) + R[i][i-1] * E_bi
        # E_bi = P[i+1][i] * E_b(i+1) + R[i][i+1] * E_fi

        self.matrix[pre_bid][bid] = self.P[fila][pre_fila]

        self.matrix[nxt_fid][fid] = self.P[fila][nxt_fila]

        self.matrix[fid][pre_fid] = self.P[pre_fila][fila]
        self.matrix[fid][bid] = self.R[pre_fila][fila]

        self.matrix[bid][nxt_bid] = self.P[nxt_fila][fila]
        self.matrix[bid][fid] = self.R[nxt_fila][fila]
    
    def _modifyMatrixRmv(self, id, pre_id, nxt_id, fila, pre_fila, nxt_fila):
        '''
        the id(s) here are (kind of ?) the index of the matrix
            (actually E_fi is in (2*id) and E_bi is in (2*id + 1) )
        the fila(s) here are the index of the filament 
            (that used for P and R)
            (fila here is not used, but i just wanna put it here to keep the params the same)
        '''

        fid = 2 * id
        bid = 2 * id + 1

        pre_fid = 2 * pre_id
        pre_bid = 2 * pre_id + 1

        nxt_fid = 2 * nxt_id
        nxt_bid = 2 * nxt_id + 1

        # E_fi = P[i-1][i] * E_f(i-1) + R[i][i-1] * E_bi
        # E_bi = P[i+1][i] * E_b(i+1) + R[i][i+1] * E_fi

        self.matrix[pre_bid][bid] = torch.tensor([0, 0, 0])
        self.matrix[pre_bid][nxt_bid] = self.P[nxt_fila][pre_fila]

        self.matrix[nxt_fid][fid] = torch.tensor([0, 0, 0])
        self.matrix[nxt_fid][pre_fid] = self.P[pre_fila][nxt_fila]

        self.matrix[fid][pre_fid] = torch.tensor([0, 0, 0])
        self.matrix[fid][bid] = torch.tensor([0, 0, 0])

        self.matrix[bid][nxt_bid] = torch.tensor([0, 0, 0])
        self.matrix[bid][fid] = torch.tensor([0, 0, 0])

    def solveEquation(self, lft_input, rht_input):

        self.outcome[0] = lft_input # E_f0
        self.outcome[3] = rht_input # E_b0

        transposed_outcome = self.outcome.permute(1, 0)
        transposed_matrix = self.matrix.permute(2, 0, 1)

        self.res = torch.linalg.solve(transposed_matrix, transposed_outcome)
        self.res = self.res.permute(1, 0)

        return self.res[1], self.res[2]
        #      E_b0       , E_fn
        #      lft_output , rht_output

    def addFila(self, fila, index):
        pass

    def rmvFila(self, fila, index):
        pass

    def mdfFila(self, fila, index):
        pass

    def randomDisturbance(self):
        pass

    def getFilaList(self):
        pass
    
    def simulatedAnnealing(self, pos, loss, epoch):
        # pos is a list-like object with length 2
        # the position of a pixel in the picture

        # loss is a function that accept a pos and return a float
        # according to the picture
        # using solveEquation

        pass

    '''

OTHER NOTES

- use jit and for statement to speed up the SA loop
- the distance (kind of loss func) should emphasize the difference in brightness
- a maximum number of layers should be set as things get crazy near (0, 0, 0)
    - maybe a minimum as well

'''