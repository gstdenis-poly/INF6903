# Description: evaluate distance between each requester's clusters and each
#              provider's clusters in database and save it into a validation
#              file.

# Include required libraries
from configurator import *
import os
import numpy as np
from scipy.spatial.distance import cosine

def validate_cluster():
  database_root = app_root + '/database'
  test_db_root = database_root + '/test'
  requesters_table = open(test_db_root + '/requester.csv', 'r').read().splitlines()
  providers_table = open(test_db_root + '/provider.csv', 'r').read().splitlines()

  results = {} # Dictionary of distances between each clusters
  for requester in requesters_table:
    requester_id = requester.split(',')[0]
    requester_db = database_root + '/' + requester_id

    requester_clusters_root = requester_db + '/clusters'
    if not os.path.exists(requester_clusters_root):
      continue

    requester_clusters = os.listdir(requester_clusters_root)
    for requester_cluster in requester_clusters:
      requester_cluster_path = requester_clusters_root + '/' + requester_cluster
      requester_cluster_centroid = open(requester_cluster_path, 'r').read().splitlines()
      requester_cluster_centroid = [float(v.split(' | ')[-1]) for v in requester_cluster_centroid]
      requester_cluster_centroid = np.array(requester_cluster_centroid)

      for provider in providers_table:
        provider_id = provider.split(',')[0]
        provider_db = database_root + '/' + provider_id

        provider_clusters_root = provider_db + '/clusters'
        if not os.path.exists(provider_clusters_root):
          continue

        provider_clusters = os.listdir(provider_clusters_root)
        for provider_cluster in provider_clusters:
          provider_cluster_path = provider_clusters_root + '/' + provider_cluster
          provider_cluster_centroid = open(provider_cluster_path, 'r').read().splitlines()
          provider_cluster_centroid = np.array([float(v.split(' | ')[-1]) for v in provider_cluster_centroid])
          provider_cluster_centroid = np.array(provider_cluster_centroid)

          # Match shape of centroids if necessary
          padding = requester_cluster_centroid.shape[0] - provider_cluster_centroid.shape[0]
          if padding > 0:
            provider_cluster_centroid = np.pad(provider_cluster_centroid, (0, padding))
          elif padding < 0:
            requester_cluster_centroid = np.pad(requester_cluster_centroid, (0, abs(padding)))

          distance = cosine(requester_cluster_centroid, provider_cluster_centroid)
          results[(requester_id, provider_id, requester_cluster, provider_cluster)] = distance

  return dict(sorted(results.items(), key=lambda item: item[1]))

distances = validate_cluster()
for k in distances:
  print('Requester ' + k[0] + ' : ' + k[2])
  print('Provider ' + k[1] + ' : ' + k[3])
  print('Distance : ' + str(distances[k]) + '\n')

# Program's main
if __name__ == '__main__':
    while True:
        validate_cluster()