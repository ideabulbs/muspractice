from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255)

    
class MetronomeSetup(models.Model):
    speed = models.FloatField()
    meter = models.IntegerField()
    duration = models.FloatField()
    increment = models.FloatField()

        
class Phrase(models.Model):
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag)
    from_position = models.FloatField()
    to_position = models.FloatField()
    loop = models.BooleanField()
    speed = models.FloatField()
    pitch = models.FloatField()
    comment = models.TextField()
    metronome = models.ForeignKey(MetronomeSetup)

    
class Repetition(models.Model):
    phrase = models.ForeignKey(Phrase)
    timestamp = models.DateTimeField()
    phrase_speed = models.FloatField()
    metronome_speed = models.FloatField()
    pitch = models.FloatField()
    comment = models.TextField()
    grade = models.IntegerField()

    
class Schedule(models.Model):
    phrase = models.ForeignKey(Phrase)
    next_repetition = models.DateTimeField()
    phrase_speed = models.FloatField()
    metronome_speed = models.FloatField()
    pitch = models.FloatField()
    comment = models.TextField()
    priority = models.FloatField()

    
class RecordingTrack(models.Model):
    filename = models.CharField(max_length=255)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()

    
class Recording(models.Model):
    phrase = models.ForeignKey(Phrase)
    tracks = models.ManyToManyField(RecordingTrack)

    
class Playback(models.Model):
    phrase = models.ForeignKey(Phrase)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    recording = models.ForeignKey(Recording)
    
# Create your models here.
