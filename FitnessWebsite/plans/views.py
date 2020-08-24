from django.shortcuts import render
from .models import FitnessPlan

# Create your views here.
def home(request):
    plans = FitnessPlan.objects.all()
    return render(request,'plans/home.html',{'plans':plans})