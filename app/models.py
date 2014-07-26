from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255)
        
class Phrase(models.Model):
    comment = models.TextField()
    filename = models.CharField(max_length=255)
    from_position = models.FloatField()
    image = models.CharField(max_length=255)
    loop = models.BooleanField()
    name = models.CharField(max_length=255)
    pitch = models.FloatField()
    speed = models.FloatField()
    tags = models.ManyToManyField(Tag)
    to_position = models.FloatField()
    volume = models.IntegerField()
    tags = models.ManyToManyField(Tag)

class MetronomeSetup(models.Model):
    duration = models.FloatField()
    meter = models.IntegerField()
    speed = models.FloatField()
    speed_increment = models.FloatField()
    volume = models.IntegerField()
    phrase = models.ForeignKey(Phrase)
    
    
class Repetition(models.Model):
    comment = models.TextField()
    grade = models.IntegerField()
    metronome_speed = models.FloatField()
    phrase = models.ForeignKey(Phrase)
    phrase_speed = models.FloatField()
    pitch = models.FloatField()
    timestamp = models.DateTimeField()

        
class Schedule(models.Model):
    comment = models.TextField()
    metronome_speed = models.FloatField()
    next_repetition = models.DateTimeField()
    phrase = models.ForeignKey(Phrase)
    phrase_speed = models.FloatField()
    pitch = models.FloatField()
    priority = models.FloatField()

# Implemented for future use:        
class RecordingTrack(models.Model):
    filename = models.CharField(max_length=255)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()

    
class Recording(models.Model):
    phrase = models.ForeignKey(Phrase)
    tracks = models.ManyToManyField(RecordingTrack)

    
class Playback(models.Model):
    end_timestamp = models.DateTimeField()
    phrase = models.ForeignKey(Phrase)
    recording = models.ForeignKey(Recording)
    start_timestamp = models.DateTimeField()
    
# Create your models here.
