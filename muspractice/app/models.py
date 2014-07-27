from django.db import models
import os


class Tag(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    
class Phrase(models.Model):
    comment = models.TextField()
    filename = models.CharField(max_length=255)
    from_position = models.FloatField()
    image = models.CharField(max_length=255)
    loop = models.BooleanField()
    name = models.CharField(max_length=255)
    pitch = models.FloatField()
    speed = models.FloatField()
    speed_increment = models.FloatField()
    tags = models.ManyToManyField(Tag)
    to_position = models.FloatField()
    volume = models.IntegerField()
    tags = models.ManyToManyField(Tag)

    def get_filename(self, path=True):
        if path:
            return self.filename
        else:
            return self.filename.split(os.sep)[-1]

    def get_short_description(self):
        if self.comment:
            lines = self.comment.split(os.linesep)
            return lines[0].strip()
        else:
            return ""
        
    def get_tagline(self):
        out = ""
        for tag in self.tags.all():
            out += tag.name + " "
        return out

    def set_tagline(self, tagline):
        tagline = tagline.strip()
        for tag in self.tags.all():
            self.tags.remove(tag)
        for tag_string in tagline.split():
            try:
                tag = Tag.objects.get(name=tag_string)
            except Tag.DoesNotExist:
                tag = Tag()
                tag.name = tag_string
                tag.save()
            self.tags.add(tag)
    
    def __unicode__(self):
        if self.id:
            return "Phrase(id=%d; name=%s; comment=%s)" % (self.id, self.name, self.comment)
        else:
            return "Phrase(name=%s; comment=%s)" % (self.name, self.comment)
    def __eq__(self, other):
        names_match = self.name == other.name
        files_match = self.filename == other.filename
        from_match = self.from_position == other.from_position
        to_match = self.to_position == other.to_position
        loop_match = self.loop == other.loop
        speed_match = self.speed == other.speed
        pitch_match = self.pitch == other.pitch
        image_match = self.image == other.image
        comment_match = self.comment == other.comment
        return names_match\
               and files_match \
               and from_match \
               and to_match \
               and loop_match \
               and speed_match \
               and pitch_match \
               and comment_match \
               and image_match

                   
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

    def __eq__(self, other):
        phrase_id_match = self.phrase.id == other.phrase.id
        date_match = self.timestamp == other.timestamp
        speed_match = self.phrase_speed == other.phrase_speed
        speed_match = self.metronome_speed == other.metronome_speed
        pitch_match = self.pitch == other.pitch
        grade_match = self.grade == other.grade
        return phrase_id_match and date_match and speed_match and pitch_match and grade_match
    
        
class Schedule(models.Model):
    comment = models.TextField()
    next_repetition = models.DateTimeField()
    phrase = models.ForeignKey(Phrase)
    priority = 0
    

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
