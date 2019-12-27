from django.db import models

# Create your models here.

# events
class Event (models.Model):
    eventId = models.AutoField(primary_key=True)
    eventTopic = models.CharField(max_length=500)
    eventDate = models.DateField()
    eventVenue = models.CharField(max_length=500)
    eventOrganizer = models.CharField(max_length=500)
    eventEnable = models.BooleanField(blank=True,default=False)
    eventFeedackEnable = models.BooleanField(blank=True,default=False)

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
        return self.firstName + " " + self.lastName


class SpeakersForEvent(models.Model):
    eventId = models.ForeignKey(Event,on_delete=models.CASCADE)
    speakerId = models.ForeignKey(Speaker,on_delete=models.CASCADE)
    speakerTopic = models.CharField(max_length=255,default="")
    speakerSequence = models.IntegerField()
    pollingEnabled = models.BooleanField(default=False)

    def __str__(self):
        #obj = Event.objects.get(pk=self.eventId)
        #print(type(obj))
        #return getattr(obj,eventTopic)
        return self.speakerId.firstName + " " + self.speakerId.lastName
#class Participant(models.Model):



class SpeakerFeedback(models.Model):
    feedbackId = models.AutoField(primary_key=True)
    eventId = models.ForeignKey(Event,on_delete=models.CASCADE)
    clientIp = models.CharField(max_length=1000,blank=True,default="")
#    participantFullName = models.CharField(max_length=255)
#    participantId = models.CharField(max_length=50)
    speakerId = models.ForeignKey(Speaker,on_delete=models.CASCADE)
    presentationStyle = models.IntegerField()
    contentRelevance = models.IntegerField()
    wentWell = models.CharField(max_length=1000,blank=True,default="")
    couldBeBetter = models.CharField(max_length=1000,blank=True,default="")
    createDateTime = models.DateTimeField(auto_now_add=True)

# speakers
    def __str__(self):
        return self.eventId.eventTopic + "," + self.speakerId.firstName + " " + self.speakerId.lastName


class EventFeedback(models.Model):
    feedbackId = models.AutoField(primary_key=True)
    eventId = models.ForeignKey(Event,on_delete=models.CASCADE)
    clientIp = models.CharField(max_length=1000,blank=True,default="")
#    participantFullName = models.CharField(max_length=255)
#    participantId = models.CharField(max_length=50)
#    speakerId = models.ForeignKey(Speaker,on_delete=models.CASCADE)
    participantFullName = models.CharField(max_length=100)
    participantIdEmail = models.EmailField()
    participantMobile =  models.CharField(max_length=15)
    contentQuality = models.IntegerField()
    contentRelevance = models.IntegerField()
    overallExperience = models.IntegerField()
    referenceable = models.BooleanField()
    likedMost = models.CharField(max_length=1000,blank=True,default="")
    couldBeBetter = models.CharField(max_length=1000,blank=True,default="")
    createDateTime = models.DateTimeField(auto_now_add=True)

# speakers
    def __str__(self):
        return self.eventId.eventTopic + "," + self.participantFullName



class QuestionType(models.Model):
    questionType = models.CharField(max_length=15)

    def __str__(self):
        return self.questionType


class PollQuestion(models.Model):
    shortDescription = models.CharField(max_length=120)
    question = models.CharField(max_length=255)
    questionType = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    answerOptions = models.CharField(max_length=1500,blank=True,default="")

    def __str__(self):
        return self.shortDescription


class EventQuestion(models.Model):
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    questionId = models.ForeignKey(PollQuestion, on_delete=models.CASCADE)
    pollingEnabled = models.BooleanField(default=False)

    def __str__(self):
        return self.eventId.eventTopic + " , " + self.questionId.shortDescription


class PollQuestionFeedback(models.Model):
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    questionId = models.ForeignKey(PollQuestion, on_delete=models.CASCADE)
    clientIp = models.CharField(max_length=1000,blank=True,default="")
    questionResponse = models.CharField(max_length=1500)
    createDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.questionResponse
