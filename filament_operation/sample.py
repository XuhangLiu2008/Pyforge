import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import pprint
from typing import List, Tuple
import os

def sample(image_path: str, new_order: bool = False) -> List[Tuple[float, list]]:
    fil_img = cv2.imread(image_path)
    if fil_img is None:
        # retry relative to this file's directory if a bare name was passed
        rel_path = os.path.join(os.path.dirname(__file__), image_path)
        fil_img = cv2.imread(rel_path)
    if fil_img is None:
        raise ValueError(f"Could not load image at '{image_path}'.")

    if fil_img.ndim != 3 or fil_img.shape[2] != 3:
        raise ValueError("Not an RGB image.")

    img_x = fil_img.shape[0]
    img_y = fil_img.shape[1]
    step_x = round(img_x / 8)
    step_y = round(img_y / 8)
    shift_x = round(step_x / 4)
    shift_y = round(step_y / 4)

    KMean_counter = 0

    def gaussian_fit_score(data):
        data = np.array(data).reshape(-1, 1)

        gm = GaussianMixture(
            n_components=1,
            covariance_type="full",
            random_state=0,
            init_params="random",
        )
        gm.fit(data)

        score = gm.score(data)
        mean = gm.means_.ravel()[0]
        return score, mean

    def categorize(data):
        nonlocal KMean_counter
        arr = np.array(data, dtype=np.float64).reshape(-1, 1)
        normal_score, normal_mean = gaussian_fit_score(arr)
        if normal_score > 0.0:
            return normal_mean

        KMean_counter += 1

        kmeans = KMeans(
            n_clusters=2,
            init="random",
            n_init=10,
            random_state=0,
        )
        kmeans.fit(arr)
        centers = kmeans.cluster_centers_.flatten()
        low_label = np.argmin(centers)
        lows = arr[kmeans.labels_ == low_label]
        low = lows[0].item()
        return low

    filament_n = []
    filament = []

    # clamp helper to stay in-bounds
    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    for i in range(1, 5):
        for j in range(1, 5):
            list_r = []
            list_g = []
            list_b = []

            x0 = clamp((i * 2 - 1) * step_x - shift_x, 0, img_x - 1)
            x1 = clamp((i * 2 - 1) * step_x + shift_x, 0, img_x)
            y0 = clamp((j * 2 - 1) * step_y - shift_y, 0, img_y - 1)
            y1 = clamp((j * 2 - 1) * step_y + shift_y, 0, img_y)

            for x in range(x0, x1):
                for y in range(y0, y1):
                    b, g, r = fil_img[x, y]
                    list_r.append(int(r))
                    list_g.append(int(g))
                    list_b.append(int(b))

            average_r = int(round(categorize(list_r)))
            average_g = int(round(categorize(list_g)))
            average_b = int(round(categorize(list_b)))
            filament_n.append([round((i - 1) * 4 + j) / 10, [average_r, average_g, average_b]])

    # DEBUG ONLY
    # This part is not working
    if new_order:
        pprint.pprint(filament_n)
        for i in range(0, 4):
            for j in range(0, 4):
                if i == 1 or i == 2:
                    index = i * 4 + j
                else:
                    index = i * 4 + (3 - j)
                filament.append(filament_n[index])
        for i in range(0, 4):
            for j in range(0, 4):
                index = i * 4 + j
                filament[index][0] = round(i * 4 + j + 1) / 10
                # pprint.pprint(filament[index])
    else:
        filament = filament_n

    # Optional: debug prints
    # print(f"KMeans was used {KMean_counter} times.")
    pprint.pp(filament)

    return filament

if __name__ == "__main__":
    filament_sample_result = sample("./filament_sample/filament03.png", new_order = True)
    pprint.pprint(filament_sample_result)