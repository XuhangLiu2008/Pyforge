import numpy as np

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

class Filament:

    def __init__(self):
        
        self.brand = ''
        self.name = ''

        self.colour = np.zeros(3, dtype = np.uint8)

        # Store fitted reflectance-like ratio per RGB channel (naming kept for compatibility)
        self.refractive_index = np.zeros(3, dtype=float)
        self.extinction_coefficient = np.zeros(3, dtype=float)

    @staticmethod
    def inverseGamma(x, gamma = 2.2):
        x /= 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** gamma
    
    R_temp2coff = {4000 : 1.8}
    G_temp2coff = {4000 : 1.0}
    B_temp2coff = {4000 : 1.4}

    def calculateCoefficients(self, samples, shown = False, color_temp = 4000):
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
            r_list.append(Filament.inverseGamma(sample[1][0]) / Filament.R_temp2coff[color_temp])
            g_list.append(Filament.inverseGamma(sample[1][1]) / Filament.G_temp2coff[color_temp])
            b_list.append(Filament.inverseGamma(sample[1][2]) / Filament.B_temp2coff[color_temp])

        reasonable_guess = [0.1, 1.5, 1.0]
        bounds = ([0.0, 0.0, 0.0], [0.9999, np.inf, 2.0])  # constrain params to physically meaningful ranges

        MAXFEV = int(5e5)

        thickness_arr = np.asarray(thickness_list, dtype=float)
        r_arr = np.asarray(r_list, dtype=float)
        g_arr = np.asarray(g_list, dtype=float)
        b_arr = np.asarray(b_list, dtype=float)

        r_coefficient, r_covariance = curve_fit(penetrateRate, thickness_arr, r_arr, p0=reasonable_guess, bounds=bounds, maxfev=MAXFEV)
        g_coefficient, g_covariance = curve_fit(penetrateRate, thickness_arr, g_arr, p0=reasonable_guess, bounds=bounds, maxfev=MAXFEV)
        b_coefficient, b_covariance = curve_fit(penetrateRate, thickness_arr, b_arr, p0=reasonable_guess, bounds=bounds, maxfev=MAXFEV)

        self.refractive_index = np.array([r_coefficient[0], g_coefficient[0], b_coefficient[0]])
        self.extinction_coefficient = np.array([r_coefficient[1], g_coefficient[1], b_coefficient[1]])

        print("R coef:", r_coefficient)
        print("G coef:", g_coefficient)
        print("B coef:", b_coefficient)

        if shown :
            d_sample = thickness_arr
            r_sample = r_arr
            g_sample = g_arr
            b_sample = b_arr

            d_data = np.linspace(0, np.max(d_sample) * 1.1, 1000)
            r_data = penetrateRate(d_data, r_coefficient[0], r_coefficient[1], r_coefficient[2])
            g_data = penetrateRate(d_data, g_coefficient[0], g_coefficient[1], g_coefficient[2])
            b_data = penetrateRate(d_data, b_coefficient[0], b_coefficient[1], b_coefficient[2])

            plt.scatter(d_sample, r_sample, c = 'r', label='R samples')
            plt.scatter(d_sample, g_sample, c = 'g', label='G samples')
            plt.scatter(d_sample, b_sample, c = 'b', label='B samples')
            plt.plot(d_data, r_data, 'r-', label='R fit')
            plt.plot(d_data, g_data, 'g-', label='G fit')
            plt.plot(d_data, b_data, 'b-', label='B fit')

            plt.xlabel('Thickness (mm)')
            plt.ylabel('Penetrate Rate')
            plt.legend()

            plt.show()

        return 

if __name__ == '__main__':
    test_filament = Filament()
    test_filament.calculateCoefficients([[0.1, [233, 222, 214]], [0.2, [234, 210, 160]], [0.3, [227, 187, 111]], [0.4, [221, 167, 81]], [0.5, [215, 147, 69]], [0.6, [208, 136, 60]], [0.7, [203, 122, 53]], [0.8, [203, 113, 50]], [0.9, [199, 103, 45]], [1.0, [193, 94, 42]], [1.1, [188, 88, 39]], [1.2, [186, 80, 38]], [1.3, [181, 75, 36]], [1.4, [177, 72, 35]], [1.5, [173, 67, 34]], [1.6, [166, 62, 32]]], True)