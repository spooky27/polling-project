from django.shortcuts import render
from django.http import HttpResponse
from submit_app.forms import PollSpeakerForm, EventFeedbackForm, PollQuestionForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Event, Speaker, SpeakerFeedback, SpeakersForEvent, EventFeedback, QuestionType, PollQuestion, EventQuestion, PollQuestionFeedback
from django.shortcuts import redirect
from .common import get_client_ip
import csv


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
        eventId = geteventinsession(request)
        if(len(eventId) < 1):
            return redirect('events')
        #eventId = request.session['eventId']

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
    client_ip = get_client_ip(request)
    if client_ip == "NOT_A_VALID_REQUEST":
        return redirect('events')
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

    eventId = geteventinsession(request)

    if(len(eventId) < 1):
        return redirect('resultsbyevent')


    enabled_speakers = SpeakersForEvent.objects.filter(pollingEnabled=True,eventId=eventId)
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
    client_ip = get_client_ip(request)
    if client_ip == "NOT_A_VALID_REQUEST":
        return redirect('events')


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
    client_ip = get_client_ip(request)
    if client_ip == "NOT_A_VALID_REQUEST":
        return redirect('events')
    eventId = geteventinsession(request)
    passedQuestionId = ""

    if(len(eventId) < 1):
        return redirect('events')


    if(request.method == 'GET') and (request.GET.get('questionId')):
        passedQuestionId = request.GET.get('questionId')
        request.session['questionId'] = passedQuestionId

    else:
        passedQuestionId = request.session['questionId']

    pollQuestion = PollQuestion.objects.get(pk=passedQuestionId)


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



@login_required(login_url='/admin/')
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

    question_response_count_dict = {'count':count}

    return JsonResponse(question_response_count_dict)


@login_required(login_url='/admin/')
def resultsbyevent(request):

    selected_event = ""
    selected_event_object = ""
    eventId = "0"

    if(request.method == 'GET') and (request.GET.get('eventId')):
        eventId = request.GET.get('eventId')
        print('event id in session: ',eventId)
        if(len(eventId) > 0):
            request.session['eventId'] = eventId

    else:
        eventId = geteventinsession(request)

    if(len(eventId) > 0):
        selected_event_object = Event.objects.get(pk=eventId)
        selected_event = selected_event_object.eventTopic

    else:
        events_list = Event.objects.filter(eventEnable=True).order_by('eventDate')
        if (events_list.count() > 0):
            eventId = events_list.first().eventId
            selected_event = events_list.first().eventTopic

    events_list = Event.objects.filter(eventEnable=True).order_by('eventDate')

    context = {'render_events':events_list, 'render_selected_event': selected_event, 'render_event_id': eventId}

    return render(request, 'submit_app/results.html',context)


@login_required(login_url='/admin/')
def reports(request):
    event_list = Event.objects.order_by('-eventDate')
    speaker_list = Speaker.objects.order_by('firstName','lastName')

    context = { 'render_event_list':event_list, 'render_speaker_list':speaker_list }

    return render(request, 'submit_app/reports.html',context)

@login_required(login_url='/admin/')
def export_csv_speakers_for_event(request):

    eventId = 0

    if(request.method == 'GET') and (request.GET.get('eventId')):
        eventId = request.GET.get('eventId')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="speakers_feedback.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Id','Event', 'Speaker', 'Speaker Email', 'Timestamp','Participant Ip','Presentation Style',
        'Content Relevance','Went Well','Could be better'])

    speakerFeedback = SpeakerFeedback.objects.filter(eventId=eventId)

    for feedback in speakerFeedback:
        feedback_to_write = []
        feedback_to_write.append(eventId)
        feedback_to_write.append(feedback.eventId.eventTopic)
        feedback_to_write.append(feedback.speakerId.firstName + " " + feedback.speakerId.lastName)
        feedback_to_write.append(feedback.speakerId.emailId)
        feedback_to_write.append(feedback.createDateTime)
        feedback_to_write.append(feedback.clientIp)
        feedback_to_write.append(feedback.presentationStyle)
        feedback_to_write.append(feedback.contentRelevance)
        feedback_to_write.append(feedback.wentWell)
        feedback_to_write.append(feedback.couldBeBetter)

        writer.writerow(feedback_to_write)

    return response



@login_required(login_url='/admin/')
def export_csv_feedback_for_event(request):

    eventId = 0

    if(request.method == 'GET') and (request.GET.get('eventId')):
        eventId = request.GET.get('eventId')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feedback_for_event.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Id','Event','Timestamp','Participant Ip','Full Name','Email','Mobile','Content Quality',
        'Content Relevance','Overall Experience','Referencable','Liked Most','Could Be Better' ])

    eventFeedback = EventFeedback.objects.filter(eventId=eventId)

    for feedback in eventFeedback:
        feedback_to_write = []
        feedback_to_write.append(eventId)
        feedback_to_write.append(feedback.eventId.eventTopic)
        feedback_to_write.append(feedback.createDateTime)
        feedback_to_write.append(feedback.clientIp)
        feedback_to_write.append(feedback.participantFullName)
        feedback_to_write.append(feedback.participantIdEmail)
        feedback_to_write.append(feedback.participantMobile)
        feedback_to_write.append(feedback.contentQuality)
        feedback_to_write.append(feedback.contentRelevance)
        feedback_to_write.append(feedback.overallExperience)
        feedback_to_write.append(feedback.referenceable)
        feedback_to_write.append(feedback.likedMost)
        feedback_to_write.append(feedback.couldBeBetter)

        writer.writerow(feedback_to_write)

    return response

@login_required(login_url='/admin/')
def export_csv_questions_for_event(request):

    eventId = 0

    if(request.method == 'GET') and (request.GET.get('eventId')):
        eventId = request.GET.get('eventId')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions_for_event.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Id','Event','Timestamp','Participant Ip','Question','Response',])

    eventFeedback = PollQuestionFeedback.objects.filter(eventId=eventId)

    for feedback in eventFeedback:
        feedback_to_write = []
        feedback_to_write.append(eventId)
        feedback_to_write.append(feedback.eventId.eventTopic)
        feedback_to_write.append(feedback.createDateTime)
        feedback_to_write.append(feedback.clientIp)
        feedback_to_write.append(feedback.questionId.question)
        feedback_to_write.append(feedback.questionResponse)

        writer.writerow(feedback_to_write)

    return response



@login_required(login_url='/admin/')
def printheaders(request):
    return render(request, 'submit_app/headers.html',{'render_headers':request.META.items()})
