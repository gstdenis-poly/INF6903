from django.contrib.auth.models import User
from django.db import models
import functools
import os
from server.settings import VAL_CLUSTERS_DIR
from statistics import mean, stdev

# Create your models here.
class Account(User):
    type = models.CharField(max_length = 20)
    company = models.CharField(default = None, null = True, blank = True, max_length = 200)
    summary = models.CharField(default = None, null = True, blank = True, max_length = 10000)
    logo = models.CharField(default = None, null = True, blank = True, max_length = 200)

class Recording(models.Model):
    id = models.CharField(max_length = 200, primary_key = True, unique = True)
    account = models.ForeignKey(Account, related_name = 'recordings', on_delete = models.CASCADE)
    title = models.CharField(default = None, blank = True, null = True, max_length = 200)
    rec_start = models.PositiveBigIntegerField(default = None, null = True)
    frame_rate = models.IntegerField(default = 15)
    frames_count = models.IntegerField(default = None, null = True)
    frames_images_count = models.IntegerField(default = None, null = True)
    mouse_events_count = models.IntegerField(default = None, null = True)
    keyboard_events_count = models.IntegerField(default = None, null = True)
    mouse_events_distance = models.FloatField(default = None, null = True)
    text_elements_count = models.IntegerField(default = None, null = True)
    text_sizes_count = models.IntegerField(default = None, null = True)
    text_sentiment_score = models.FloatField(default = None, null = True)

    # Return relevant solutions for recording according to its related results file.
    # Solution is relevant if:
    #   - Its rank in results file is better than the count of accounts of different
    #     type than the account of given recording.
    #   - Its score is higher than 0.0.
    #   - Its score is higher or equal to the average score + 1x the standard deviation.
    def get_relevant_solutions(self):
        results_file_path = VAL_CLUSTERS_DIR + self.id + '.txt'
        if not os.path.isfile(results_file_path):
            return []

        results_file = open(results_file_path, 'r')
        results_file_lines = results_file.read().splitlines()
        results_file.close()

        results_score = [float(l.split('|')[1]) for l in results_file_lines]
        results_scores_avg = mean(results_score)
        results_scores_sd = stdev(results_score) if len(results_score) > 1 else 0.0
        opposite_acc_type = 'provider' if self.account.type == 'requester' else 'requester'
        results_score_count_max = len(Account.objects.all().filter(type = opposite_acc_type))
        print('Scores avg: ' + str(results_scores_avg) + ' | Scores stdev: ' + str(results_scores_sd))

        solutions = []
        for i, line in enumerate(results_file_lines):
            line_infos = line.split('|')
            score = float(line_infos[1])

            print(line_infos[0] + ': ' + line_infos[1])

            if i == results_score_count_max or \
               score == 0.0 or score < (results_scores_avg + results_scores_sd):
                break

            solutions += [Recording.objects.get(id = line_infos[0])]

        return solutions
    
    # Get all ergonomic comparison criterias of recording
    def get_ergonomic_criterias(self):
        criterias = [self.mouse_events_count]
        criterias += [self.keyboard_events_count]
        criterias += [self.mouse_events_distance]
        criterias += [self.text_elements_count / self.frames_images_count]
        criterias += [self.text_sizes_count / self.frames_images_count]
        criterias += [self.text_sentiment_score / self.frames_images_count]
        criterias += [self.frames_count / self.frame_rate * 1000000000] # Duration in nanoseconds

        return criterias
    
    # Compare ergonomic criterias of two given solutions. Sorting is from highest 
    # to lowest scores.
    @staticmethod
    def cmp_solutions_score(s1, s2):
        s1_criterias = s1.get_ergonomic_criterias()
        s2_criterias = s2.get_ergonomic_criterias()

        s1_score, s2_score = 0, 0
        for s1_criteria, s2_criteria in zip(s1_criterias, s2_criterias):
            if s1_criteria > s2_criteria:
                s2_score += 1
            elif s2_criteria > s1_criteria:
                s1_score += 1
        
        print(s1.id + ': ' + str(s1_score) + ' | ' + s2.id + ': ' + str(s2_score))
        return -1 if s1_score > s2_score else 0 if s1_score == s2_score else 1

class Monitor(models.Model):
    recording = models.ForeignKey(Recording, related_name = 'monitors', on_delete = models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

class MouseEvent(models.Model):
    recording = models.ForeignKey(Recording, related_name = 'mouse_events', on_delete = models.CASCADE)
    stamp = models.PositiveBigIntegerField()
    button = models.CharField(max_length = 20)
    x = models.FloatField()
    y = models.FloatField()

class KeyboardEvent(models.Model):
    recording = models.ForeignKey(Recording, related_name = 'keyboard_events', on_delete = models.CASCADE)
    stamp = models.PositiveBigIntegerField()
    key = models.CharField(max_length = 20)
    
class Request(models.Model):
    account = models.ForeignKey(Account, related_name = 'requests', on_delete = models.CASCADE)
    recordings = models.ManyToManyField(Recording, related_name = 'requests')
    
    # Return relevant solutions for request according to relevant solutions of each of
    # its recordings. A request's solution is relevant if it contains at least one relevant
    # recording's solution.
    def get_relevant_solutions(self):
        solutions = {}
        for recording in self.recordings.all():
            for solution in recording.get_relevant_solutions():
                candidate_id = solution.account.username
                if candidate_id in solutions:
                    solutions[candidate_id].add(solution)
                else:
                    solutions[candidate_id] = {solution}

        return solutions

    # Compare ergonomic score of two given request's solutions. The ergonomic score of a
    # request's solution is considered better if the total of the reversed ranks of its
    # recordings' scores is higher than the total of the reversed ranks of the compared
    # request's solution's recordings' scores. Sorting is from highest to lowest scores.
    @staticmethod 
    def cmp_solutions_score(s1, s2):
        solutions = list(s1[1]) + list(s2[1])
        cmp_key = functools.cmp_to_key(Recording.cmp_solutions_score)
        solutions.sort(key = cmp_key, reverse = True)

        s1_score, s2_score = 0, 0
        for i, solution in enumerate(solutions):
            if solution.account.username == s1[0]:
                s1_score += i
            else:
                s2_score += i

        print(s1[0] + ': ' + str(s1_score) + ' | ' + s2[0] + ': ' + str(s2_score))
        return -1 if s1_score > s2_score else 0 if s1_score == s2_score else 1

class Favorite(models.Model):
    solution = models.ForeignKey(Recording, on_delete = models.CASCADE)

class RecordingFavorite(Favorite):
    recording = models.ForeignKey(Recording, related_name = 'favorites', on_delete = models.CASCADE)

class RequestFavorite(Favorite):
    request = models.ForeignKey(Request, related_name = 'favorites', on_delete = models.CASCADE)