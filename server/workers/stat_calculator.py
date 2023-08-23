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

    # Build training dataset from requesters favorites. Dataset is formatted as
    # a dict with key corresponding to a tuple of recording(s) id (single for a
    # recording favorite and multiple for a request favorite) and a value
    # corresponding to a list of solutions provided for the recording/request
    # and marked as favorites by the requester.
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

    # Calculate an optimized deviation from requesters favorites. This deviation
    # is the one that offers the best precision+recall score before the optimization 
    # reached its timeout. The values in train dataset are considered the ground 
    # truth and are compared with a comparison dataset to evaluate the precision 
    # and recall. The comparison dataset is built on each iteration with the  
    # solutions provided for recordings in train dataset keys and having a score 
    # above the average score + the current deviation. The deviation to evaluate 
    # is incremented at each iteration, a current deviation is returned as the 
    # best deviation before timeout if the minimum wanted precision+recall score 
    # is reached.
    def calculate_fav_dev(self):
        if self.curr_clusters_validation_count == self.clusters_validation_count and \
           self.curr_rec_favorites_count == self.rec_favorites_count and \
           self.curr_req_favorites_count == self.req_favorites_count:
            return
        
        train_dataset = self.build_fav_train_dataset() # Training dataset
        timeout = 15 * 1000000000 # 10 seconds in nanoseconds
        min_pr_score = 2.0 # Minimum wanted precision+recall score
        start_time = time.time_ns() # Start time in nanoseconds
        elapsed_time = 0 # Elapsed time from start time in nanoseconds
        best_pr_score = 0.0 # Best precision+recall score
        best_fav_dev = 0.0 # Fav deviation with best precision+recall score
        curr_fav_dev = 0.0 # Current validated fav deviation

        while best_pr_score < min_pr_score and elapsed_time < timeout:
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

                    for line in rec_cluster_val_lines:
                        line_parts = line.split('|')
                        if float(line_parts[1]) < (scores_mean + curr_fav_dev):
                            break
                        cmp_dataset[key] += [line_parts[0]]
            # Calc precision+recall score of comparison dataset with train dataset
            true_positives, false_positives, false_negatives = 0, 0, 0
            for key in cmp_dataset:
                for prediction in cmp_dataset[key]:
                    if prediction in train_dataset[key]:
                        true_positives += 1
                    else:
                        false_positives += 1
                for truth in train_dataset[key]:
                    if truth not in cmp_dataset[key]:
                        false_negatives += 1
            curr_pr_score = 0.0 # Current evaluated precision+recall score
            if true_positives > 0:
                curr_precision = true_positives / (true_positives + false_positives)
                curr_recall = true_positives / (true_positives + false_negatives)
                curr_pr_score = curr_precision + curr_recall
            # Update best precision+recall score and best fav deviation
            if curr_pr_score > best_pr_score:
                best_pr_score = curr_pr_score
                best_fav_dev = curr_fav_dev
                print(cmp_dataset)
                print(best_pr_score)
                print(best_fav_dev)
            # Increment fav dev and elapsed time for next iteration
            curr_fav_dev += 0.1
            elapsed_time = time.time_ns() - start_time

        Statistic(id = 'fav_dev', value = best_fav_dev).save()

    # Calculate average standard deviation of solutions provided for all
    # requesters recordings.
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