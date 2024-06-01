from django.shortcuts import render
from django.http import HttpResponse



def home(request):
    return HttpResponse('Home page')


def grafana_dashboard(request):
    return render(request, 'grafana_dashboard.html')



# Create your views here.
