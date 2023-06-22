# Description: evaluate distance between each requester's clusters and each
#              provider's clusters in database and save it into a validation
#              file.

# Include required libraries
from configurator import *
import os
import numpy as np
from scipy.spatial.distance import cosine
import shutil

# Return cluster's centroid of given cluster file
def get_cluster_centroid(cluster_file_path):
    cluster_centroid = open(cluster_file_path, 'r').read().splitlines()
    cluster_centroid = [float(v.split(' | ')[-1]) for v in cluster_centroid]
    cluster_centroid = np.array(cluster_centroid) 

    return cluster_centroid

# Return cosine distance between two clusters' centroids
def get_centroids_distance(centroid1, centroid2):
    padding = centroid1.shape[0] - centroid2.shape[0]
    if padding > 0:
        centroid2 = np.pad(centroid2, (0, padding))
    elif padding < 0:
        centroid1 = np.pad(centroid1, (0, abs(padding)))

    return cosine(centroid1, centroid2)

# Return account type of given account name
def get_account_type(acc_name):
    acc_type = None

    acc_file_path = accounts_folder + acc_name + '.txt'
    acc_file = open(acc_file_path, 'r')
    for line in acc_file.read().splitlines():
        line_infos = line.split('|')
        if line_infos[0] == 'acc_type':
            acc_type = line_infos[1]
            break

    return acc_type

# Save temporary cluster files to database and return True if at
# least one cluster file was saved to database
def save_clusters():
    cluster_saved = False
    for cluster_file_name in os.path.listdir(clusters_folder):
        cluster_file_path = clusters_folder + cluster_file_name
        cluster_final_file_path = os.path.splitext(cluster_file_path)[0] + '.final'
        if not os.path.isfile(cluster_final_file_path):
            continue
              
        shutil.move(cluster_file_path, res_clusters_folder)
        os.remove(cluster_final_file_path) # Remove .final file
        cluster_saved = True

    return cluster_saved

# Program's main function
def validate_cluster():
    clusters_to_validate = save_clusters()
    if not clusters_to_validate:
       return
    
    for cluster_file_name in os.path.listdir(res_clusters_folder):
        cluster_file_path = res_clusters_folder + cluster_file_name
        cluster_centroid = get_cluster_centroid(cluster_file_path)

        recording_id = os.path.splitext(cluster_file_name)[0]
        acc_name = recording_id.split('-')[0]
        acc_type = get_account_type(acc_name)

        for cmp_cluster_file_name in os.path.listdir(clusters_folder):
            if cmp_cluster_file_name == cluster_file_name:
                continue

            cmp_cluster_file_path = clusters_folder + cmp_cluster_file_name
            cmp_recording_id = os.path.splitext(cmp_cluster_file_path)[0]
            cmp_acc_name = cmp_recording_id.split('-')[0]
            cmp_acc_type = get_account_type(cmp_acc_name)

            # Compare clusters only if accounts not of same type
            if cmp_acc_type == acc_type:
                continue

            cmp_cluster_centroid = get_cluster_centroid(cmp_cluster_file_path)
            distance = get_centroids_distance(cluster_centroid, cmp_cluster_centroid)
            
            cluster_val_file_path = val_clusters_folder + cluster_file_name
            cluster_val_file = open(cluster_val_file_path, 'w')
            cluster_val_file.write('recording_id|' + cmp_recording_id + '\n')
            cluster_val_file.write('distance|' + distance)
            cluster_val_file.close()

# Program's main
if __name__ == '__main__':
    while True:
        validate_cluster()