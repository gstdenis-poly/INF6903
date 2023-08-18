# Description: calculate global statistics over database and save those 
#              in a database's table.

# Include required libraries
from configurator import *
import os
from statistics import mean, stdev
import time
from web.models import Recording, Request, RecordingFavorite, RequestFavorite, Statistic

class StatCalculator:
    rec_favorites_count, curr_rec_favorites_count = 0, 0
    req_favorites_count, curr_req_favorites_count = 0, 0
    clusters_validation_count, curr_clusters_validation_count = 0, 0

    def build_fav_train_dataset(self):
        dataset = {}

        for recording in Recording.objects.all():
            if recording.account.type == 'provider':
                continue

            recording_id = tuple([recording.id])

            dataset[recording_id] = []
            for favorite in recording.favorites.all():
                dataset[recording_id] += [favorite.solution.id]

        for request in Request.objects.all():
            recordings_id = tuple(sorted([r.id for r in request.recordings.all()]))

            dataset[recordings_id] = []
            for favorite in request.favorites.all():
                dataset[recordings_id] += [favorite.solution.id]

        return dataset

    def calculate_fav_dev(self):
        if self.curr_clusters_validation_count == self.clusters_validation_count and \
           self.curr_rec_favorites_count == self.rec_favorites_count and \
           self.curr_req_favorites_count == self.req_favorites_count:
            return
        
        train_dataset = self.build_fav_train_dataset() # Training dataset
        timeout = 10 * 1000000000 # 10 seconds in nanoseconds
        min_precision = 1.0 # Minimum precision wanted
        start_time = time.time_ns() # Start time in nanoseconds
        elapsed_time = 0 # Elapsed time from start time in nanoseconds
        best_precision = 0.0 # Best precision obtained
        curr_precision = 0.0 # Current evaluated precision
        best_fav_dev = 0.0 # Fav deviation with best precision
        curr_fav_dev = 0.0 # Current validated fav deviation

        while best_precision < min_precision and elapsed_time < timeout:
            # Build comparison dataset
            cmp_dataset = {}
            for key in train_dataset:
                cmp_dataset[key] = []
                for recording in key:
                    rec_cluster_val_file = open(val_clusters_folder + recording + '.txt', 'r')
                    rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
                    rec_cluster_val_file.close()

                    scores = [float(l.split('|')[1]) for l in rec_cluster_val_lines]
                    scores_mean = mean(scores)
                    scores_stdev = (stdev(scores) if len(scores) > 1 else 0.0)

                    for line in rec_cluster_val_lines:
                        line_parts = line.split('|')
                        if float(line_parts[1]) < (scores_mean + scores_stdev + curr_fav_dev):
                            break
                        cmp_dataset[key] += [line_parts[0]]
            # Calc precision of comparison dataset with train dataset
            true_positives, false_positives = 0, 0
            for key in cmp_dataset:
                for positive in cmp_dataset[key]:
                    if positive in train_dataset[key]:
                        true_positives += 1
                    else:
                        false_positives += 1
            if true_positives > 0:
                curr_precision = true_positives / (true_positives + false_positives)
            # Update best precision and best fav deviation
            if curr_precision > best_precision:
                best_precision = curr_precision
                best_fav_dev = curr_fav_dev
            # Increment fav dev and elapsed time for next iteration
            curr_fav_dev += 0.01
            elapsed_time = time.time_ns() - start_time

        Statistic(id = 'fav_dev', value = best_fav_dev).save()

    def calculate_avg_stdev(self):
        if self.curr_clusters_validation_count == self.clusters_validation_count:
            return

        recs_stdev = []
        for recording in Recording.objects.all():
            if recording.account.type == 'provider':
                continue

            rec_cluster_val_file = open(val_clusters_folder + recording.id + '.txt', 'r')
            rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
            rec_cluster_val_file.close()

            rec_cluster_val_scores = [float(l.split('|')[1]) for l in rec_cluster_val_lines]
            if len(rec_cluster_val_scores) > 1:
                recs_stdev += [stdev(rec_cluster_val_scores)]

        if recs_stdev:
            Statistic(id = 'avg_stdev', value = mean(recs_stdev)).save()    

    # Program main function
    def calculate_stat(self):
        self.curr_rec_favorites_count = len(RecordingFavorite.objects.all())
        self.curr_req_favorites_count = len(RequestFavorite.objects.all())
        self.curr_clusters_validation_count = len(os.listdir(val_clusters_folder))

        self.calculate_fav_dev()
        self.calculate_avg_stdev()

        self.rec_favorites_count = self.curr_rec_favorites_count
        self.req_favorites_count = self.curr_req_favorites_count
        self.clusters_validation_count = self.curr_clusters_validation_count

# Program's main
if __name__ == '__main__':
    stat_calculator = StatCalculator()
    while True:
        stat_calculator.calculate_stat()