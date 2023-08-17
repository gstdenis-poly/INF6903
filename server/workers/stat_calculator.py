# Description: calculate global statistics over database and save those 
#              in a database's table.

# Include required libraries
from configurator import *
import os
from statistics import mean
from web.models import Recording, Request, RecordingFavorite, RequestFavorite, Statistic

rec_favorites_count = 0
req_favorites_count = 0
clusters_validation_count = 0

def calculate_rec_fav_avg_diff_from_avg_score():
    rec_fav_diffs = []
    for recording in Recording.objects.all():
        rec_cluster_val_file = open(val_clusters_folder + recording.id + '.txt', 'r')
        rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
        rec_cluster_val_file.close()

        rec_favorites_max_score = 0.0
        for favorite in recording.favorites.all():
            for line in rec_cluster_val_lines:
                line_parts = line.split('|')
                if line_parts[0] == favorite.solution.id:
                    favorite_score = float(line_parts[1])
                    if favorite_score > rec_favorites_max_score:
                        rec_favorites_max_score = favorite_score
                    break

        if rec_favorites_max_score == 0.0:
            break

        rec_avg_score = mean([float(l.split('|')[1]) for l in rec_cluster_val_lines])
        rec_fav_diffs += [rec_favorites_max_score - rec_avg_score]

    Statistic(id = 'rec_fav_avg_diff_from_avg_score', value = mean(rec_fav_diffs)).save()

def calculate_req_fav_avg_diff_from_avg_score():
    req_fav_diffs = []
    for request in Request.objects.all():
        req_favorites_max_diff = 0.0
        for favorite in request.favorites.all():
            for recording in request.recordings.all():
                rec_cluster_val_file = open(val_clusters_folder + recording.id + '.txt', 'r')
                rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
                rec_cluster_val_file.close()

                rec_avg_score = mean([float(l.split('|')[1]) for l in rec_cluster_val_lines])

                for line in rec_cluster_val_lines:
                    line_parts = line.split('|')
                    if line_parts[0] == favorite.solution.id:
                        favorite_diff = (float(line_parts[1]) - rec_avg_score)
                        if favorite_diff > req_favorites_max_diff:
                            req_favorites_max_diff = favorite_diff
                        break
                        
        if req_favorites_max_diff == 0.0:
            break

        req_fav_diffs += [req_favorites_max_diff]

    Statistic(id = 'req_fav_avg_diff_from_avg_score', value = mean(req_fav_diffs)).save()

# Calculate statistic of average favorites difference with
# average score of their recording's cluster validation
def calculate_fav_avg_diff_from_avg_score():
    rec_favorites = RecordingFavorite.objects.all()
    req_favorites = RequestFavorite.objects.all()
    clusters_validation = os.listdir(val_clusters_folder)

    curr_rec_favorites_count = len(rec_favorites)
    curr_req_favorites_count = len(req_favorites)
    curr_clusters_validation_count = len(clusters_validation)

    if curr_clusters_validation_count > clusters_validation_count:
        calculate_rec_fav_avg_diff_from_avg_score()
        calculate_req_fav_avg_diff_from_avg_score()
    elif curr_rec_favorites_count > rec_favorites_count:
        calculate_rec_fav_avg_diff_from_avg_score()
    elif curr_req_favorites_count > req_favorites_count:
        calculate_req_fav_avg_diff_from_avg_score()

    clusters_validation_count = curr_clusters_validation_count
    rec_favorites_count = curr_rec_favorites_count
    req_favorites_count = curr_req_favorites_count

# Program main function
def calculate_stat():
    calculate_fav_avg_diff_from_avg_score()

# Program's main
if __name__ == '__main__':
    while True:
        calculate_stat()