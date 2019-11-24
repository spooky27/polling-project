from django.contrib import admin

# Register your models here.

# Register models here

from submit_app.models import Event, Speaker, SpeakerFeedback

admin.site.register(Event)
admin.site.register(Speaker)
admin.site.register(SpeakerFeedback)
