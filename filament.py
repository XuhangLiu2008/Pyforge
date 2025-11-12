import cv2
import numpy as np

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

class Filament:

    def __init__(self):
        
        self.brand = ''
        self.name = ''

        self.colour = np.zeros(3, dtype = np.uint8)

        self.refrative_index = np.zeros(3)
        self.extinction_coefficient = np.zeros(3)

    def calculateCoefficients(self, samples, shown = False):
        # samples is a list of [thickness, colour]
        # colour should be np.uint8 array with size 3
        
        def penetrateRate(thickness, refractive_ratio, extinction_coefficient, enlarge_factor):
            penetrateRateInside = np.exp(-1 * extinction_coefficient * thickness)
            return enlarge_factor * (1 - refractive_ratio) ** 2 * penetrateRateInside / (1 - refractive_ratio ** 2 * penetrateRateInside ** 2)
            # return enlarge_factor * penetrateRateInside
        
        thickness_list = []
        r_list = []
        g_list = []
        b_list = []

        for sample in samples:
            thickness_list.append(sample[0])
            r_list.append(sample[1][0] / 255.0)
            g_list.append(sample[1][1] / 255.0)
            b_list.append(sample[1][2] / 255.0)

        reasonable_guess = [0.1, 1.5, 0.5]

        MAXFEV = int(1e5)

        r_coefficient, r_covariance = curve_fit(penetrateRate, thickness_list, r_list, p0 = reasonable_guess, maxfev = MAXFEV)
        g_coefficient, g_covariance = curve_fit(penetrateRate, thickness_list, g_list, p0 = reasonable_guess, maxfev = MAXFEV)
        b_coefficient, b_covariance = curve_fit(penetrateRate, thickness_list, b_list, p0 = reasonable_guess, maxfev = MAXFEV)

        self.refractive_index = np.array([r_coefficient[0], g_coefficient[0], b_coefficient[0]])
        self.extinction_coefficient = np.array([r_coefficient[1], g_coefficient[1], b_coefficient[1]])

        print(r_coefficient)
        print(g_coefficient)
        print(b_coefficient)

        if shown :
            d_sample = np.array(thickness_list)
            r_sample = np.array(r_list)
            g_sample = np.array(g_list)
            b_sample = np.array(b_list)

            d_data = np.linspace(0, np.max(d_sample) * 1.1, 1000)
            r_data = penetrateRate(d_data, r_coefficient[0], r_coefficient[1], r_coefficient[2])
            g_data = penetrateRate(d_data, g_coefficient[0], g_coefficient[1], r_coefficient[2])
            b_data = penetrateRate(d_data, b_coefficient[0], b_coefficient[1], r_coefficient[2])

            plt.scatter(d_sample, r_sample, c = 'r')
            plt.scatter(d_sample, g_sample, c = 'g')
            plt.scatter(d_sample, b_sample, c = 'b')
            plt.plot(d_data, r_data, 'r-')
            plt.plot(d_data, g_data, 'g-')
            plt.plot(d_data, b_data, 'b-')

            plt.xlabel('Thickness (mm)')
            plt.ylabel('Penetrate Rate')

            plt.show()

        return 

if __name__ == '__main__':

    test_filament = Filament()
    test_filament.calculateCoefficients([[0.1, [245, 254, 250]], [0.2, [130, 120, 124]], [0.4, [67, 60, 62]], [0.8, [34, 37, 28]], [1.6, [20, 13, 16]]], True)