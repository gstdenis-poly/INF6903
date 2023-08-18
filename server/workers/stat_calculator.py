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
    smart_stdev_train_dataset = {
        'richbank-1690216267308128170': ['office365-1690215618610561557',
                                         'libreoffice-1690213562387230010',
                                         'optibus-1690471293632541631'],
        'uinsurances-1690217158458021147': ['optibus-1690471293632541631',
                                            'office365-1690215618610561557',
                                            'libreoffice-1690213562387230010'],
        'canadapost-1690469973482655850': [],
        'office365-1690215722576562207': ['uinsurances-1690217281299334200',
                                          'richbank-1690216393879738319'],
        'libreoffice-1690213864828106713': ['richbank-1690216343948675325',
                                            'uinsurances-1690217222160671516'],
        'ivu-1690312720116058813': ['uinsurances-1690314483725517698'],
        'optibus-1690471293632541631': ['uinsurances-1690217158458021147',
                                        'richbank-1690216267308128170'],
        'transit-1690472193137807594': []
    }

    def calculate_rec_fav_avg_diff_from_avg_score(self):
        rec_fav_diffs = []
        for recording in Recording.objects.all():
            if recording.account.type == 'provider':
                continue

            rec_cluster_val_file = open(val_clusters_folder + recording.id + '.txt', 'r')
            rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
            rec_cluster_val_file.close()

            rec_favorites_min_score = 99.9
            for favorite in recording.favorites.all():
                for line in rec_cluster_val_lines:
                    line_parts = line.split('|')
                    if line_parts[0] == favorite.solution.id:
                        favorite_score = float(line_parts[1])
                        if favorite_score < rec_favorites_min_score:
                            rec_favorites_min_score = favorite_score
                        break

            if rec_favorites_min_score == 99.9:
                rec_fav_diffs += [0.0]
            else:
                rec_avg_score = mean([float(l.split('|')[1]) for l in rec_cluster_val_lines])
                rec_fav_diffs += [rec_favorites_min_score - rec_avg_score]

        return rec_fav_diffs

    def calculate_req_fav_avg_diff_from_avg_score(self):
        req_fav_diffs = []
        for request in Request.objects.all():
            req_favorites_min_diff = 99.9
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
                            if favorite_diff < req_favorites_min_diff:
                                req_favorites_min_diff = favorite_diff
                            break
            
            if req_favorites_min_diff == 99.9:
                req_fav_diffs += [0.0]
            else:
                req_fav_diffs += [req_favorites_min_diff]

        return req_fav_diffs

    # Calculate statistic of average favorites difference with
    # average score of their recording's cluster validation
    def calculate_fav_avg_diff_from_avg_score(self):
        fav_diffs = []
        if self.curr_clusters_validation_count != self.clusters_validation_count:
            fav_diffs += self.calculate_rec_fav_avg_diff_from_avg_score()
            fav_diffs += self.calculate_req_fav_avg_diff_from_avg_score()
        elif self.curr_rec_favorites_count != self.rec_favorites_count:
            fav_diffs += self.calculate_rec_fav_avg_diff_from_avg_score()
        elif self.curr_req_favorites_count != self.req_favorites_count:
            fav_diffs += self.calculate_req_fav_avg_diff_from_avg_score()

        if fav_diffs:
            Statistic(id = 'fav_avg_diff_from_avg_score', value = mean(fav_diffs)).save()

    def calculate_smart_stdev(self):
        if self.curr_clusters_validation_count == self.clusters_validation_count:
            return

        timeout = 10 * 1000000000 # 10 seconds in nanoseconds
        min_precision = 1.0 # Minimum precision wanted
        start_time = time.time_ns() # Start time in nanoseconds
        elapsed_time = 0 # Elapsed time from start time in nanoseconds
        best_precision = 0.0 # Best precision obtained
        best_smart_stdev = 0.0 # Smart stdev with best precision
        curr_smart_stdev = 0.0 # Current validated smart stdev

        while best_precision < min_precision and elapsed_time < timeout:
            # Build comparison dataset
            cmp_dataset = {}
            for recording in self.smart_stdev_train_dataset:
                rec_cluster_val_file = open(val_clusters_folder + recording + '.txt', 'r')
                rec_cluster_val_lines = rec_cluster_val_file.read().splitlines()
                rec_cluster_val_file.close()
                rec_cluster_val_scores = [float(l.split('|')[1]) for l in rec_cluster_val_lines]
                rec_cluster_val_scores_mean = mean(rec_cluster_val_scores)
                
                cmp_dataset[recording] = []
                for line in rec_cluster_val_lines:
                    line_parts = line.split('|')
                    if float(line_parts[1]) >= (rec_cluster_val_scores_mean + curr_smart_stdev):
                        break
                    cmp_dataset[recording] += [line_parts[0]]
            # Calc precision of comparison dataset with train dataset
            true_positives, false_positives = 0, 0
            for recording in cmp_dataset:
                for positive in cmp_dataset[recording]:
                    if positive in self.smart_stdev_train_dataset[recording]:
                        true_positives += 1
                    else:
                        false_positives += 1
            curr_precision = true_positives / (true_positives + false_positives)
            # Update best precision and best smart stdev
            if curr_precision > best_precision:
                best_precision = curr_precision
                best_smart_stdev = curr_smart_stdev
            # Increment smart stdev and elapsed time for next iteration
            curr_smart_stdev += 0.1
            elapsed_time = time.time_ns() - start_time

        Statistic(id = 'smart_stdev', value = best_smart_stdev).save()

    # Program main function
    def calculate_stat(self):
        self.curr_rec_favorites_count = len(RecordingFavorite.objects.all())
        self.curr_req_favorites_count = len(RequestFavorite.objects.all())
        self.curr_clusters_validation_count = len(os.listdir(val_clusters_folder))

        self.calculate_smart_stdev()
        self.calculate_fav_avg_diff_from_avg_score()

        self.rec_favorites_count = self.curr_rec_favorites_count
        self.req_favorites_count = self.curr_req_favorites_count
        self.clusters_validation_count = self.curr_clusters_validation_count

# Program's main
if __name__ == '__main__':
    stat_calculator = StatCalculator()
    while True:
        stat_calculator.calculate_stat()