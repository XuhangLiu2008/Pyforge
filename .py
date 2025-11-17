import numpy as np
import cv2

import torch

from filament import Filament

class Pyforge:

    def __init__(self, available_filaments, thickness, picture):

        self.available_filaments = available_filaments
        self.thickness = thickness
        self.picture = picture

        self.intensity_table = np.zeros((len(self.available_filaments)+1, len(self.available_filaments)+1), dtype=float)
        # intensity_table[i][j] is the multiple of the intensity when light travels from i-th filament to j-th filament
        # I_right_after_j = intensity_table[i][j] * I_right_after_i
        # I_right_after_i = intensity_table[j][i] * I_right_after_j
        # the last filament is always the air

        for i in range(len(self.available_filaments)):
            for j in range(len(self.available_filaments)):
                # exp(-K_j * d) * (1 - R)
                # R = ( (n1 - n2) / (n1 + n2) ) ^ 2
                fila1 = self.available_filaments[i]
                fila2 = self.available_filaments[j]
                R = ( (fila1.refractive_index - fila2.refractive_index) / (fila1.refractive_index + fila2.refractive_index) ) ** 2
                self.intensity_table[i][j] = np.exp(- fila2.extinction_coefficient * self.thickness) * (1-R)
        
        for i in range(len(self.available_filaments)):
            n = self.available_filaments[i].refractive_index
            R = ( (n - 1) / (n + 1) ) ** 2

            self.intensity_table[i][len(self.available_filaments)] = (1 - R)

            self.intensity_table[len(self.available_filaments)][i] = (1 - R) * np.exp(- self.available_filaments[i].extinction_coefficient * self.thickness)

