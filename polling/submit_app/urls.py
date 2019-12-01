from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.events, name='events'),
    path('submit_app/eventspeakers', views.eventspeakers, name='eventspeakers'),
    re_path(r'^submit_app/pollspeaker$', views.pollspeaker, name='pollspeaker'),
    re_path(r'^submit_app/viewresults$', views.viewresults, name='viewresults'),
    re_path(r'^submit_app/pollevent$', views.pollevent, name='pollevent'),
    re_path(r'^ajax/getpollcount$', views.getpollcount, name='getpollcount'),

]
