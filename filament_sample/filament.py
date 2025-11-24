import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

image_path = "filament02.png"
fil_img = cv2.imread(image_path)
if fil_img is None:
    print("Error: Could not load image.")
else:
    print("Image loaded successfully.")
    print(f"Image shape: {fil_img.shape}")

img_x = fil_img.shape[0]
img_y = fil_img.shape[1]
step_x = round(img_x / 8)
step_y = round(img_y / 8)
shift_x = round(step_x / 4)
shift_y = round(step_y / 4)
print(f"step_x: {step_x}, step_y: {step_y}, shift_x: {shift_x}, shift_y: {shift_y}")

if fil_img.shape[2] != 3:
    print("Error: Not a RGB image.")

array = []

KMean_counter = 0

def gaussian_fit_score(data):
    data = np.array(data).reshape(-1, 1)

    gm = GaussianMixture(
        n_components=1,
        covariance_type="full",
        random_state=0,
        init_params="random",  # <- no internal KMeans
    )
    gm.fit(data)

    # higher (less negative) means closer to normal
    score = gm.score(data)
    mean = gm.means_.ravel()[0]
    return score, mean

def categorize(data):
    global KMean_counter
    arr = np.array(data, dtype=np.float64).reshape(-1, 1)
    '''
    if arr.size == 0:
        return arr.flatten()
    if np.unique(arr).size < 2:
        return arr.flatten()
    '''
    normal_score, normal_mean = gaussian_fit_score(arr)
    if normal_score > 0.0:
        print(arr.flatten())
        return normal_mean
    
    KMean_counter += 1

    kmeans = KMeans(
        n_clusters=2,
        init="random",   # <- avoids the k-means++ potential / matmul
        n_init=10,
        random_state=0,
    )
    kmeans.fit(arr)
    centers = kmeans.cluster_centers_.flatten()
    low_label = np.argmin(centers)     # cluster whose mean is smallest
    lows = arr[kmeans.labels_ == low_label]
    low = lows[0].item()        # or lows[0].item()
    return low

for i in range(1, 5):
    for j in range(1, 5):
        list_r = []
        list_g = []
        list_b = []

        counter = 0
        for x in range((i * 2 - 1) * step_x - shift_x, (i * 2 - 1) * step_x + shift_x):
            for y in range((j * 2 - 1) * step_y - shift_y, (j * 2 - 1) * step_y + shift_y):
                b, g, r = fil_img[x, y]
                list_r.append(int(r))
                list_g.append(int(g))
                list_b.append(int(b))
                counter += 1
        
        average_r = int(round(categorize(list_r)))
        average_g = int(round(categorize(list_g)))
        average_b = int(round(categorize(list_b)))
        array.append([round((i - 1) * 4 + j) / 10, [average_r, average_g, average_b]])

print(f"KMeans was used {KMean_counter} times.")
print(array)