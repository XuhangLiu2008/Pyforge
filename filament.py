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

    @staticmethod
    def RGB2RelativeIntensity(color, gamma = 2.2, color_temp = 4000):
        return np.array([Filament.inverseGamma(color[0]) / Filament.R_temp2coff[color_temp], 
                         Filament.inverseGamma(color[1]) / Filament.G_temp2coff[color_temp], 
                         Filament.inverseGamma(color[2]) / Filament.B_temp2coff[color_temp]])

    def calculateCoefficients(self, samples, shown = False, color_temp = 4000):
        # samples is a list of [thickness, colour]
        # colour should be np.uint8 array with size 3

        def penetrateRate(thickness, refractive_ratio, extinction_coefficient, enlarge_factor):
            penetrateRateInside = np.exp(-1 * extinction_coefficient * thickness)
            return enlarge_factor * (1 - refractive_ratio) ** 2 * penetrateRateInside / (1 - refractive_ratio ** 2 * penetrateRateInside ** 2)
        
        def combinedCoeff(thickness, R_r, K_r, R_g, K_g, R_b, K_b, enlarge_factor):
            # thickness here should be an array with 3 identical copies
            # to fit all coeffs together
            length = len(thickness) // 3
            res = np.zeros_like(thickness)
            res[:length] = penetrateRate(thickness[:length], R_r, K_r, enlarge_factor)
            res[length:2*length] = penetrateRate(thickness[length:2*length], R_g, K_g, enlarge_factor)
            res[2*length:] = penetrateRate(thickness[2*length:], R_b, K_b, enlarge_factor)

            return res
        
        thickness_list = []
        r_list = []
        g_list = []
        b_list = []

        for sample in samples:
            thickness_list.append(sample[0])
            intensity = Filament.RGB2RelativeIntensity(sample[1])
            r_list.append(intensity[0])
            g_list.append(intensity[1])
            b_list.append(intensity[2])

        reasonable_guess = [0.1, 1.5, 0.1, 1.5, 0.1, 1.5, 1.0]
        bounds = ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.9999, np.inf, 0.9999, np.inf, 0.9999, np.inf, np.inf])
        # constrain params to physically meaningful ranges

        MAXFEV = int(5e5)

        thickness_arr = np.asarray(thickness_list * 3, dtype=float)
        target_arr = np.asarray(r_list + g_list + b_list, dtype=float)

        coefficient, covariance = curve_fit(combinedCoeff, thickness_arr, target_arr, p0=reasonable_guess, bounds=bounds, maxfev=MAXFEV)

        r_coefficient = np.array([coefficient[0], coefficient[1], coefficient[6]])
        g_coefficient = np.array([coefficient[2], coefficient[3], coefficient[6]])
        b_coefficient = np.array([coefficient[4], coefficient[5], coefficient[6]])

        self.refractive_index = np.array([r_coefficient[0], g_coefficient[0], b_coefficient[0]])
        self.extinction_coefficient = np.array([r_coefficient[1], g_coefficient[1], b_coefficient[1]])

        print("R coef:", r_coefficient)
        print("G coef:", g_coefficient)
        print("B coef:", b_coefficient)

        if shown :
            d_sample = np.asarray(thickness_list, dtype=float)
            r_sample = np.asarray(r_list, dtype=float)
            g_sample = np.asarray(g_list, dtype=float)
            b_sample = np.asarray(b_list, dtype=float)

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
    test_filament.calculateCoefficients([[0.1, [231, 219, 212]], [0.2, [228, 203, 153]], [0.3, [220, 180, 104]], [0.4, [219, 165, 79]], [0.5, [213, 144, 66]], [0.6, [205, 132, 57]], [0.7, [201, 119, 51]], [0.8, [201, 111, 48]], [0.9, [197, 102, 44]], [1.0, [192, 92, 40]], [1.1, [186, 86, 37]], [1.2, [184, 78, 36]], [1.3, [179, 73, 34]], [1.4, [175, 69, 33]], [1.5, [171, 65, 32]], [1.6, [164, 59, 29]]], True)