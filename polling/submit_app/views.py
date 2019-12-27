from django.shortcuts import render
from django.http import HttpResponse
from submit_app.forms import PollSpeakerForm, EventFeedbackForm, PollQuestionForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Event, Speaker, SpeakerFeedback, SpeakersForEvent, EventFeedback, QuestionType, PollQuestion, EventQuestion, PollQuestionFeedback
from django.shortcuts import redirect


#REDIRECT_URL_FOR_EVENT: 'submit_app/events.html'
#REDIRECT_URL_FOR_SPEAKER: 'submit_app/eventspeakers.html'

def events(request):
    events_list = Event.objects.filter(eventEnable=True).order_by('eventDate')

    return render(request, 'submit_app/events.html',{'render_events':events_list})


def eventspeakers(request):

    eventId = ""


    if(request.method == 'GET') and (request.GET.get('eventId')):
        eventId = request.GET.get('eventId')
        request.session['eventId'] = eventId
        #speakerName = Speaker.objects.get(pk=passedSpeakerId)
        print("Event Id from event speakers, if block: ",eventId)
    else:
        if(len(eventId) < 1):
            return redirect('events')
        eventId = request.session['eventId']

    # check if event is enabled
    isEventEnabled = Event.objects.filter(eventId=eventId,eventEnable=True)
    if not isEventEnabled:
        return redirect('events')

    # Chcek if eventFeedackEnable is enabled
    isEventFeedbackEnabled = Event.objects.filter(eventId=eventId,eventFeedackEnable=True)

    #check if question is enabled

    questions_list = EventQuestion.objects.filter(eventId=eventId,pollingEnabled=True)

    # provide speakers list for event
    event_speakers_list = SpeakersForEvent.objects.filter(eventId=eventId).order_by('speakerSequence')


    return render(request, 'submit_app/eventspeakers.html',{'render_speakers':event_speakers_list, 'render_event_feedback_enabled':isEventFeedbackEnabled, 'render_poll_questions':questions_list })

def pollspeaker(request):
    #event_speakers_list = SpeakersForEvent.objects.order_by('speakerSequence')
    #if request.METHOD == "POST":
    #g = GeoIP()
    client_ip = request.META['REMOTE_ADDR']
#    lat,long = g.lat_lon(client_ip)
    print(client_ip)

    poll_submitted = False
    passedSpeakerId = ""
    speakerName = ""


    eventId = geteventinsession(request)

    if(len(eventId) < 1):
        return redirect('events')

    if(request.method == 'GET') and (request.GET.get('speakerId')):
        passedSpeakerId = request.GET.get('speakerId')
        request.session['speakerId'] = passedSpeakerId
        speakerName = Speaker.objects.get(pk=passedSpeakerId)
        print(speakerName, " in if")
    else:
        passedSpeakerId = request.session['speakerId']
        print(passedSpeakerId, " in else")

    if(request.method == 'POST'):

        print('BEFORE PollSpeakerForm creation!!!')
        poll_speaker_form = PollSpeakerForm(data=request.POST,req=request)
        print('AFTER PollSpeakerForm creation!!!')

        if poll_speaker_form.is_valid():

            record_feedback = poll_speaker_form.save(commit=False)
            record_feedback.eventId = Event.objects.get(pk=eventId)
            record_feedback.clientIp = client_ip
            record_feedback.speakerId = Speaker.objects.get(pk=passedSpeakerId)

            # check for event, speaker, client ip combination
            #hasAlreadyPolled = SpeakerFeedback.objects.filter(speakerId=record_feedback.speakerId,eventId=record_feedback.eventId,clientIp=client_ip)
            #if hasAlreadyPolled:
        #        print('matching IP address!!')
                #raise poll_speaker_form.ValidationError("You have already submitted your feedback for this speaker or event")

        #    else:
            record_feedback.save();
            poll_submitted = True
        else:
            print('errors in form')
    else:
        poll_speaker_form = PollSpeakerForm(req=request)

    return render(request, 'submit_app/pollspeaker.html',{'render_poll_speaker_form':poll_speaker_form,'poll_submitted':poll_submitted, 'speaker_id':passedSpeakerId, 'speaker_name':speakerName })


@login_required(login_url='/admin/')
def viewresults(request):
    # get list of enabled speakers
    enabled_speakers = SpeakersForEvent.objects.filter(pollingEnabled=True)
    context = {}
    dict_to_render = {}
    event_feedback = []

    event_id_for_speaker = ""

    if(enabled_speakers):
        for speaker in enabled_speakers:
            feedbackForSpeaker = SpeakerFeedback.objects.filter(eventId=speaker.eventId,speakerId=speaker.speakerId)
            dict_to_render[speaker] = feedbackForSpeaker.count()
            event_id_for_speaker = speaker.eventId
            # get event feedbackId


        print(dict_to_render)
        event_feedback.append(EventFeedback.objects.filter(eventId=event_id_for_speaker).count())


        context = { 'dict_to_render': dict_to_render, 'event_feedback_render': event_feedback }



    return render(request,'submit_app/viewresults.html',context)


'''
def get_geo_details(request):
  g = GeoIP()
  client_ip = request.META['REMOTE_ADDR']
  lat,long = g.lat_lon(client_ip)
  return render_to_response('home_page_tmp.html',locals())
'''

def getpollcount(request):
    #speakerId = request.GET.get('speakerId')
    #print(speakerId)
    enabled_speakers = SpeakersForEvent.objects.filter(pollingEnabled=True)
    context = {}
    speaker_feedback_count_dict = {}
    event_id = ""

    if(enabled_speakers):
        for speaker in enabled_speakers:
            feedbackForSpeaker = SpeakerFeedback.objects.filter(eventId=speaker.eventId,speakerId=speaker.speakerId)
            speaker_feedback_count_dict[speaker.speakerId.speakerId] = feedbackForSpeaker.count()
            event_id = speaker.eventId
    #        print(speaker_feedback_count_dict)
    #        print('event id is: ',event_id)


        event_feedback_count = EventFeedback.objects.filter(eventId=event_id).count()
        print('event feedback count is: ', event_feedback_count)
        speaker_feedback_count_dict['event_id'] = event_feedback_count

        print(speaker_feedback_count_dict)

    return JsonResponse(speaker_feedback_count_dict)


def pollevent(request):

    poll_submitted = False
    client_ip = request.META['REMOTE_ADDR']
    eventId = geteventinsession(request)

    if(len(eventId) < 1):
        return redirect('events')


    if(request.method == 'POST'):
        event_feedbadk_form = EventFeedbackForm(data=request.POST,req=request)

        if event_feedbadk_form.is_valid():
            record_feedback = event_feedbadk_form.save(commit=False)
            record_feedback.eventId = Event.objects.get(pk=eventId)
            record_feedback.clientIp = client_ip
            record_feedback.save();
            poll_submitted = True

    else:
        event_feedbadk_form = EventFeedbackForm(req=request)

    return render(request, 'submit_app/pollevent.html',{'render_event_feedback_form':event_feedbadk_form,'poll_submitted':poll_submitted,})


def geteventinsession(request):
    return request.session.get('eventId','')


def getspeakerinsession(request):
    return request.session['speakerId']




def pollquestion(request):


    poll_question_submitted = False
    pollQuestion = ""
    client_ip = request.META['REMOTE_ADDR']
    eventId = geteventinsession(request)

    if(len(eventId) < 1):
        return redirect('events')


    if(request.method == 'GET') and (request.GET.get('questionId')):
        passedQuestionId = request.GET.get('questionId')
        request.session['questionId'] = passedQuestionId
        pollQuestion = PollQuestion.objects.get(pk=passedQuestionId)
        print(passedQuestionId, " in if")
    else:
        passedQuestionId = request.session['questionId']
        print(passedQuestionId, " in else")


    if(request.method == 'POST'):
        poll_feedbadk_form = PollQuestionForm(data=request.POST,req=request)

        if poll_feedbadk_form.is_valid():
            record_poll_feedback = poll_feedbadk_form.save(commit=False)
            record_poll_feedback.eventId = Event.objects.get(pk=eventId)
            record_poll_feedback.clientIp = client_ip
            record_poll_feedback.questionId = PollQuestion.objects.get(pk=passedQuestionId)
            record_poll_feedback.save();
            poll_question_submitted = True

    else:
        poll_feedbadk_form = PollQuestionForm(req=request)

    return render(request, 'submit_app/pollquestion.html',{'render_poll_feedbadk_form':poll_feedbadk_form,'poll_question_submitted':poll_question_submitted, 'render_poll_question' : pollQuestion})


@login_required(login_url='/admin/')
def viewpollquestionresults(request):


    totalResponses = 0
    pollQuestion = ""
    context = {}
    dict_to_render = {}
    question_responses = []

    eventId = geteventinsession(request)

    if(len(eventId) < 1):
        return redirect('events')

    enabled_poll_questions = EventQuestion.objects.filter(pollingEnabled=True, eventId=eventId)

    #TODO: put in check for multiple enabled questions

    event_id_for_speaker = ""

    if(enabled_poll_questions):
        for question in enabled_poll_questions:
            pollQuestion = question.questionId.question
            all_feedback = PollQuestionFeedback.objects.filter(eventId=question.eventId,questionId=question.questionId)
            questionId = question.questionId.pk

            feedback_list = []
            for single_feedback in all_feedback:
                feedback_list.append(single_feedback)
                totalResponses = totalResponses+1

                print(single_feedback)

            dict_to_render[question] = feedback_list

            # get event feedbackId


        context = { 'dict_to_render': dict_to_render, 'total_responses_render': totalResponses,'poll_question_render': pollQuestion, 'question_id_render': questionId}

    return render(request, 'submit_app/viewpollquestionresults.html',context)




def getquestionresponsecount(request):

    questionId = request.GET.get('questionId', None)
    print('question id from ajax call: ',questionId)

    count = 0;
    question_response_count_dict = {}

    eventId = geteventinsession(request)

    if(len(eventId) < 1):
        count = "0"
    else:
        enabled_poll_questions = PollQuestionFeedback.objects.filter(eventId=eventId,questionId=questionId)
        count = enabled_poll_questions.count()
        print('current count in views function: ' + str(count))

    question_response_count_dict = {'count':count}

    return JsonResponse(question_response_count_dict)
