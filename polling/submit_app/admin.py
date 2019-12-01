from django.contrib import admin

# Register your models here.

# Register models here

from submit_app.models import Event, Speaker, SpeakerFeedback, SpeakersForEvent, EventFeedback

admin.site.register(Event)
admin.site.register(Speaker)
admin.site.register(SpeakerFeedback)
admin.site.register(SpeakersForEvent)
admin.site.register(EventFeedback)
