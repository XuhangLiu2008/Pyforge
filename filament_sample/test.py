import numpy as np
from sklearn.cluster import KMeans

data = np.array([10, 11, 10, 5, 5, 6, 5, 10, 11, 4]).reshape(-1, 1)

kmeans = KMeans(n_clusters=2, random_state=0)
kmeans.fit(data)

print("Cluster centers:", kmeans.cluster_centers_)
print("Labels:", kmeans.labels_)

lowValues = data[kmeans.labels_ == 0]

print("Low values:", lowValues.flatten())