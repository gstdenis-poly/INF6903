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
    cluster_centroid = [float(v.split('|')[-1]) for v in cluster_centroid]
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
    acc_file_lines = acc_file.read().splitlines()
    acc_file.close()

    print(acc_name)

    for line in acc_file_lines:
        line_infos = line.split('|')
        if line_infos[0] == 'acc_type':
            acc_type = line_infos[1]
            break

    print(acc_type)

    return acc_type

# Save temporary cluster files to database and return True if at
# least one cluster file was saved to database
def save_clusters():
    cluster_saved = False
    for file_name in os.listdir(clusters_folder):
        file_path = clusters_folder + file_name
        file_path_parts = os.path.splitext(file_path)
        if file_path_parts[1] != '.final':
            continue

        cluster_file_path = file_path_parts[0] + '.txt'
        shutil.move(cluster_file_path, res_clusters_folder)
        os.remove(file_path) # Remove .final file
        cluster_saved = True

    return cluster_saved

# Program's main function
def validate_cluster():
    clusters_to_validate = save_clusters()
    if not clusters_to_validate:
       return
    
    for cluster_file_name in os.listdir(res_clusters_folder):
        print(cluster_file_name)
        cluster_file_path = res_clusters_folder + cluster_file_name
        cluster_centroid = get_cluster_centroid(cluster_file_path)

        recording_id = os.path.splitext(cluster_file_name)[0]
        print(recording_id)
        acc_name = recording_id.split('-')[0]
        acc_type = get_account_type(acc_name)

        cluster_val_file_path = val_clusters_folder + cluster_file_name
        cluster_val_file = open(cluster_val_file_path, 'w')

        for cmp_cluster_file_name in os.listdir(res_clusters_folder):
            print(cmp_cluster_file_name)
            if cmp_cluster_file_name == cluster_file_name:
                continue

            cmp_cluster_file_path = clusters_folder + cmp_cluster_file_name
            cmp_recording_id = os.path.splitext(cmp_cluster_file_name)[0]
            print(cmp_recording_id)
            cmp_acc_name = cmp_recording_id.split('-')[0]
            cmp_acc_type = get_account_type(cmp_acc_name)
            print('allo!')
            print(acc_type + ' | ' + cmp_acc_type)

            # Compare clusters only if accounts not of same type
            if cmp_acc_type == acc_type:
                continue

            cmp_cluster_centroid = get_cluster_centroid(cmp_cluster_file_path)
            distance = get_centroids_distance(cluster_centroid, cmp_cluster_centroid)
            cluster_val_file.write(cmp_recording_id + '|' + str(distance) + '\n')
        
        cluster_val_file.close()

# Program's main
if __name__ == '__main__':
    while True:
        validate_cluster()