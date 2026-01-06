# home/views.py
from django.shortcuts import render

from django.shortcuts import render

def home_view(request):
    return render(request, "home.html")
