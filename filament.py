import cv2
import numpy as np

class Filament:

    def __init__(self):
        
        self.brand = ''
        self.name = ''

        self.colour = np.zeros(3, dtype = np.uint8)

        self.refrative_index = np.zeros(3)
        self.extinction_coefficient = np.zeros(3)

    def calculateCoefficients(self, samples):
        # samples is a list of [thickness, colour]
        # colour should be np.uint8 array with size 3
        pass