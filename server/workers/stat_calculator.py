# Description: calculate global statistics over database and save those 
#              in a database's table.

# Include required libraries
from configurator import *
import os
from statistics import mean, stdev
from web.models import Recording, Request, RecordingFavorite, RequestFavorite, Statistic

class StatCalculator:
    rec_favorites_count = 0
    req_favorites_count = 0
    clusters_validation_count = 0

    def calculate_rec_fav_avg_diff_from_avg_score(self):
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
                        print(favorite_score)
                        if favorite_score > rec_favorites_max_score:
                            rec_favorites_max_score = favorite_score
                        break

            print(rec_favorites_max_score)
            if rec_favorites_max_score == 0.0:
                continue

            rec_avg_score = mean([float(l.split('|')[1]) for l in rec_cluster_val_lines])
            rec_fav_diffs += [rec_favorites_max_score - rec_avg_score]

        print(rec_fav_diffs)
        return rec_fav_diffs

    def calculate_req_fav_avg_diff_from_avg_score(self):
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
                            print(favorite_diff)
                            if favorite_diff > req_favorites_max_diff:
                                req_favorites_max_diff = favorite_diff
                            break
            
            print(req_favorites_max_diff)  
            if req_favorites_max_diff == 0.0:
                continue

            req_fav_diffs += [req_favorites_max_diff]

        print(req_fav_diffs)
        return req_fav_diffs

    # Calculate statistic of average favorites difference with
    # average score of their recording's cluster validation
    def calculate_fav_avg_diff_from_avg_score(self):
        curr_rec_favorites_count = len(RecordingFavorite.objects.all())
        curr_req_favorites_count = len(RequestFavorite.objects.all())
        curr_clusters_validation_count = len(os.listdir(val_clusters_folder))

        fav_diffs = []
        if curr_clusters_validation_count > self.clusters_validation_count:
            fav_diffs += self.calculate_rec_fav_avg_diff_from_avg_score()
            fav_diffs += self.calculate_req_fav_avg_diff_from_avg_score()
        elif curr_rec_favorites_count > self.rec_favorites_count:
            fav_diffs += self.calculate_rec_fav_avg_diff_from_avg_score()
        elif curr_req_favorites_count > self.req_favorites_count:
            fav_diffs += self.calculate_req_fav_avg_diff_from_avg_score()

        if fav_diffs:
            Statistic(id = 'fav_avg_diff_from_avg_score', value = mean(fav_diffs)).save()

        self.clusters_validation_count = curr_clusters_validation_count
        self.rec_favorites_count = curr_rec_favorites_count
        self.req_favorites_count = curr_req_favorites_count

    def calculate_avg_stdev(self):
        curr_clusters_validation_count = len(os.listdir(val_clusters_folder))
        if curr_clusters_validation_count == self.clusters_validation_count:
            return

        recs_stdev = []
        for recording in Recording.objects.all():
            rec_cluster_val_file = open(val_clusters_folder + recording.id + '.txt', 'r')
            rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
            rec_cluster_val_file.close()

            rec_cluster_val_scores = [float(l.split('|')[1]) for l in rec_cluster_val_lines]
            if len(rec_cluster_val_scores) > 1:
                recs_stdev += [stdev(rec_cluster_val_scores)]

        if recs_stdev:
            Statistic(id = 'avg_stdev', value = mean(recs_stdev)).save()

        self.clusters_validation_count = curr_clusters_validation_count

    # Program main function
    def calculate_stat(self):
        self.calculate_avg_stdev()
        self.calculate_fav_avg_diff_from_avg_score()

# Program's main
if __name__ == '__main__':
    stat_calculator = StatCalculator()
    while True:
        stat_calculator.calculate_stat()