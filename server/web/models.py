from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Account(User):
    type = models.IntegerField(default = 0)
    company = models.CharField(max_length = 200)
    summary = models.CharField(max_length = 10000)
    logo = models.CharField(max_length = 200)

class Recording(models.Model):
    id = models.CharField(max_length = 200, primary_key = True, unique = True)
    account = models.ForeignKey(Account, related_name = 'recordings', on_delete = models.CASCADE)
    title = models.CharField(max_length = 200)
    rec_start = models.PositiveBigIntegerField()
    frame_rate = models.IntegerField(default = 15)
    frames_count = models.IntegerField()
    frames_images_count = models.IntegerField()
    mouse_events_count = models.IntegerField()
    keyboard_events_count = models.IntegerField()
    mouse_events_distance = models.FloatField()
    text_elements_count = models.IntegerField()
    text_sizes_count = models.IntegerField()
    text_sentiment_score = models.FloatField()

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
    recordings = models.ManyToManyField(Recording)
    candidates = models.ManyToManyField(Account)