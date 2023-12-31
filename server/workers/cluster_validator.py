# Description: evaluate score between each requester's clusters and each
#              provider's clusters in database and save it into a validation
#              file.

# Include required libraries
from configurator import *
import os
import numpy as np
from scipy.spatial.distance import cosine
import shutil
from web.models import Account

# Return a dict of vectors per token according to given cluster file.
def get_cluster_vectors(cluster_file_path):
    cluster_file = open(cluster_file_path, 'r')
    cluster_file_lines = cluster_file.read().splitlines()
    cluster_file.close()

    cluster_vectors = {}
    for line in cluster_file_lines:
        line_parts = line.split('|')
        cluster_vectors[line_parts[0]] = float(line_parts[1])

    return cluster_vectors

# Return the centroid the given cluster files considering only the tokens 
# that exist in both of the given cluster files.
def get_clusters_centroid(cluster1_file_path, cluster2_file_path):
    cluster1_vectors = get_cluster_vectors(cluster1_file_path)
    cluster2_vectors = get_cluster_vectors(cluster2_file_path)

    tokens = list(set(cluster1_vectors.keys()) & set(cluster2_vectors.keys()))

    cluster1_centroid, cluster2_centroid = [], []
    for token in tokens:
        cluster1_centroid += [float(cluster1_vectors[token])]
        cluster2_centroid += [float(cluster2_vectors[token])]

    return np.array(cluster1_centroid), np.array(cluster2_centroid)

# Get account's type of given account's name
def get_account_type(acc_name):
    try:
        account = Account.objects.get(username = acc_name)
        return account.type
    except Account.DoesNotExist:
        return None

# Save temporary cluster files to database and return True if at
# least one cluster file was saved to database
def save_clusters():
    cluster_saved = False
    for file_name in os.listdir(clusters_folder):
        file_path = clusters_folder + file_name
        file_name_parts = os.path.splitext(file_name)
        if file_name_parts[1] != '.final':
            continue

        res_cluster_file_path = res_clusters_folder + file_name_parts[0] + '.txt'
        if os.path.isfile(res_cluster_file_path):
            os.remove(res_cluster_file_path) # Delete res cluster file if already exists

        cluster_file_path = clusters_folder + file_name_parts[0] + '.txt'
        shutil.move(cluster_file_path, res_cluster_file_path)
        os.remove(file_path) # Remove .final file
        cluster_saved = True

    return cluster_saved

# Program's main function
def validate_cluster():
    clusters_to_validate = save_clusters()
    if not clusters_to_validate:
       return
    
    for cluster_file_name in os.listdir(res_clusters_folder):
        cluster_file_path = res_clusters_folder + cluster_file_name

        recording_id = os.path.splitext(cluster_file_name)[0]
        acc_name = recording_id.split('-')[0]
        acc_type = get_account_type(acc_name)

        cluster_val_file_path = val_clusters_folder + cluster_file_name
        cluster_val_file = open(cluster_val_file_path, 'w')

        scores = {} # Dictionary of scores per recording id
        for cmp_cluster_file_name in os.listdir(res_clusters_folder):
            if cmp_cluster_file_name == cluster_file_name:
                continue

            cmp_cluster_file_path = res_clusters_folder + cmp_cluster_file_name
            cmp_recording_id = os.path.splitext(cmp_cluster_file_name)[0]
            cmp_acc_name = cmp_recording_id.split('-')[0]
            cmp_acc_type = get_account_type(cmp_acc_name)

            # Compare clusters only if accounts not of same type
            if cmp_acc_type == acc_type:
                continue

            c1, c2 = get_clusters_centroid(cluster_file_path, cmp_cluster_file_path)
            distance = cosine(c1, c2) if c1.size > 0 else 1.0
            scores[cmp_recording_id] = 1.0 - distance + c1.size
        
        for item in sorted(scores.items(), key = lambda item: item[1], reverse = True):
            cluster_val_file.write(item[0] + '|' + str(item[1]) + '\n')

        cluster_val_file.close()

# Program's main
if __name__ == '__main__':
    while True:
        validate_cluster()