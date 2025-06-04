from django.shortcuts import render

# Create your views here.

def home(request):
    """
    Главная страница сайта о касатках и их звуках
    """
    # Шаблон home.html должен находиться в папке templates. Если папки нет, создайте её в корне приложения или проекта.
    return render(request, 'home.html')
