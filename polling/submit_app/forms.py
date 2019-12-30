from django import forms
from django.contrib.auth.models import User
from submit_app.models import SpeakerFeedback, EventFeedback, Event, Speaker, PollQuestionFeedback
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .common import get_client_ip


CHOICES = [
    ('5','Excellent'),
    ('4','Very Good'),
    ('3','Good'),
    ('2','Average'),
    ('1','Poor'),
]

ERRORS = {
    'SPEAKER_FEEDBACK_FROM_SAME_IP': 'It seems you have already submitted feedback for this speaker',
    'QUESTION_FEEDBACK_FROM_SAME_IP': 'It seems you have already submitted your response for this question',
    'EVENT_FEEDBACK_FROM_SAME_IP': 'It seems you have already submitted your feedback for this event',
}


class PollSpeakerForm(forms.ModelForm):
    presentationStyle = forms.ChoiceField(widget=forms.RadioSelect( attrs={'class': 'form-check-input' } ), choices=CHOICES, label='How would you rate the presentation style of the speaker? ')
    contentRelevance = forms.ChoiceField(widget=forms.RadioSelect ( attrs={'class': 'form-check-input' } ), choices=CHOICES, label='How would you rate the relevance of the content presented?  ')

    class Meta():
        model = SpeakerFeedback
        fields = ['presentationStyle','contentRelevance','wentWell','couldBeBetter']
        widgets = {
            'wentWell': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
            'couldBeBetter': forms.Textarea(attrs={'cols': 60, 'rows': 5}),

        }
        labels = {
            #'presentationStyle': _('Presentation style of speaker:'),
            #'contentRelevance': _('Relavence of content presented:'),
            'wentWell': _('What went well? :'),
            'couldBeBetter': _('What could have been better? :'),
        }


    def __init__(self, *args, **kwargs):
      self.req = kwargs.pop('req')  # cache the user object you pass in
      super(PollSpeakerForm, self).__init__(*args, **kwargs)  # and carry on to init the form


    def clean(self):
        cleaned_data = super().clean()

        if(settings.RESTRICT_MULTIPLE_POLLS):

            event_id = self.req.session.get('eventId','')
            speaker_id = self.req.session.get('speakerId','')
        #    client_ip = self.req.META['REMOTE_ADDR']
            client_ip = get_client_ip(self.req)

            eventObj = Event.objects.get(pk=event_id)
            speakerObj = Speaker.objects.get(pk=speaker_id)

            matchingRecords = SpeakerFeedback.objects.filter(speakerId=speakerObj,eventId=eventObj,clientIp=client_ip)
            if matchingRecords.count() > 0:
                print("FOUND matching records!!!")
                raise forms.ValidationError(ERRORS['SPEAKER_FEEDBACK_FROM_SAME_IP'])


        return self.cleaned_data



class EventFeedbackForm(forms.ModelForm):
    contentQuality = forms.ChoiceField(widget=forms.RadioSelect( attrs={'class': 'form-check-input' } ), choices=CHOICES,)
    contentRelevance = forms.ChoiceField(widget=forms.RadioSelect ( attrs={'class': 'form-check-input' } ), choices=CHOICES,)
    overallExperience = forms.ChoiceField(widget=forms.RadioSelect ( attrs={'class': 'form-check-input' } ), choices=CHOICES,)


    class Meta():
        model = EventFeedback
        fields = ['participantFullName','participantIdEmail','participantMobile','contentQuality','contentRelevance',
            'overallExperience','likedMost','couldBeBetter', 'referenceable']

        widgets = {
            'likedMost': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
            'couldBeBetter': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
        #    'contentQuality': forms.MultipleChoiceField(attrs={'choices=CHOICES'}),

        }
        labels = {
            #'presentationStyle': _('Presentation style of speaker:'),
            #'contentRelevance': _('Relavence of content presented:'),
            'wentWell': _('What went well? :'),
            'couldBeBetter': _('What could have been better? :'),
        }


    def __init__(self, *args, **kwargs):
      self.req = kwargs.pop('req')  # cache the user object you pass in
      super(EventFeedbackForm, self).__init__(*args, **kwargs)  # and carry on to init the form


    def clean(self):
        cleaned_data = super().clean()

        if(settings.RESTRICT_MULTIPLE_POLLS):

            event_id = self.req.session.get('eventId','')
            #speaker_id = self.req.session.get('speakerId','')
        #    client_ip = self.req.META['REMOTE_ADDR']
            client_ip = get_client_ip(self.req)

            eventObj = Event.objects.get(pk=event_id)
            #speakerObj = Speaker.objects.get(pk=speaker_id)

            matchingRecords = EventFeedback.objects.filter(eventId=eventObj,clientIp=client_ip)
            if matchingRecords.count() > 0:
                print("FOUND matching records!!!")
                raise forms.ValidationError(ERRORS['EVENT_FEEDBACK_FROM_SAME_IP'])



        return self.cleaned_data


class PollQuestionForm(forms.ModelForm):
    class Meta():
        model = PollQuestionFeedback
        fields = ['questionResponse']

        widgets = {
                'questionResponse': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            }

        labels = {
                #'presentationStyle': _('Presentation style of speaker:'),
                #'contentRelevance': _('Relavence of content presented:'),
                'questionResponse': '',
                }

    def __init__(self, *args, **kwargs):
      self.req = kwargs.pop('req')  # cache the user object you pass in
      super(PollQuestionForm, self).__init__(*args, **kwargs)  # and carry on to init the form


    def clean(self):
        cleaned_data = super().clean()

        if(settings.RESTRICT_MULTIPLE_POLLS):

            event_id = self.req.session.get('eventId','')
            client_ip = get_client_ip(self.req)
            questionId = self.req.session.get('questionId')

            eventObj = Event.objects.get(pk=event_id)

            matchingRecords = PollQuestionFeedback.objects.filter(eventId=eventObj,clientIp=client_ip, questionId=questionId)
            if matchingRecords.count() > 0:
                raise forms.ValidationError(ERRORS['QUESTION_FEEDBACK_FROM_SAME_IP'])


        return self.cleaned_data
