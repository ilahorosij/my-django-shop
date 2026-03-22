from django.shortcuts import render
from django.http import HttpResponse


from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render


def home(request):
    return render(request, 'index.html') 


def author(request):
    return render(request, 'author.html')


def about(request):
    return render(request, 'about.html')