from django.db import models

# Create your models here.

# events
class Event (models.Model):
    eventId = models.AutoField(primary_key=True)
    eventTopic = models.CharField(max_length=500)
    eventDate = models.DateField()
    eventVenue = models.CharField(max_length=500)
    eventOrganizer = models.CharField(max_length=500)

    def __str__(self):
        return self.eventTopic


class Speaker (models.Model):
    speakerId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    emailId = models.EmailField()
    linkedIn = models.URLField(blank=True,default='')
    presentationStyleAverage = models.IntegerField(blank=True,default=-1)
    qualityOfContentAverage = models.IntegerField(blank=True,default=-1)
#    photo = models.bin

    def __str__(self):
        return self.firstName



class SpeakerFeedback(models.Model):
    eventId = models.ForeignKey(Event,on_delete=models.CASCADE)
    participantFullName = models.CharField(max_length=255)
    participantIdentifier = models.CharField(max_length=50)
    speakerId = models.ForeignKey(Speaker,on_delete=models.CASCADE)
# speakers
    def __str__(self):
        return self.participantFullName
