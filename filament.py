import cv2
import numpy as np

class Filament:

    def __init__(self):

        self.colour = np.zeros(3, dtype = np.uint8)

        self.refrative_index = np.zeros(3)
        self.extinction_coefficient = np.zeros(3)