from django.shortcuts import render
from .models import Voices

# Create your views here.

def home(request):
    """
    Главная страница сайта о касатках и их звуках
    """
    sounds = Voices.objects.all()
    return render(request, 'home.html', {'sounds': sounds})

def sound_library(request):
    """
    Страница библиотеки звуков касаток
    """
    sounds = Voices.objects.all()
    return render(request, 'sound_library.html', {'sounds': sounds})

def about(request):
    """
    Страница 'О касатках'
    """
    return render(request, 'about.html')
