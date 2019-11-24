from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

#def submit(request):
#    return HttpResponse("Test page from polling app")


def submit(request):
    return render(request, 'submit_app/select.html')
