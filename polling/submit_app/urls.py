from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.events, name='events'),
    path('submit_app/eventspeakers', views.eventspeakers, name='eventspeakers'),
    re_path(r'^submit_app/pollspeaker$', views.pollspeaker, name='pollspeaker'),
    re_path(r'^submit_app/pollquestion$', views.pollquestion, name='pollquestion'),
    re_path(r'^submit_app/viewresults$', views.viewresults, name='viewresults'),
    re_path(r'^submit_app/viewpollquestionresults$', views.viewpollquestionresults, name='viewpollquestionresults'),
    re_path(r'^submit_app/pollevent$', views.pollevent, name='pollevent'),
    re_path(r'^ajax/getpollcount$', views.getpollcount, name='getpollcount'),
    re_path(r'^ajax/getquestionresponsecount$', views.getquestionresponsecount, name='getquestionresponsecount'),
    re_path(r'^results$', views.resultsbyevent, name='resultsbyevent'),
    re_path(r'^reports$', views.reports, name='reports'),
    re_path(r'^speakers_for_event$', views.export_csv_speakers_for_event, name='export_csv_speakers_for_event'),
    re_path(r'^feedback_for_event$', views.export_csv_feedback_for_event, name='export_csv_feedback_for_event'),
    re_path(r'^questions_for_event$', views.export_csv_questions_for_event, name='export_csv_questions_for_event'),
    re_path(r'^headers$', views.printheaders, name='printheaders'),

]
