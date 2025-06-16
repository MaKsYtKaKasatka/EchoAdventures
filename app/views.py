from django.shortcuts import render, get_object_or_404
from .models import Voices, Game, Test, Question, Answer, QuestionTest
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .services import AchievementService
from .django_models import UserProgress, UserAchievement, UserSound

# Create your views here.

def home(request):
    """
    Главная страница сайта о касатках и их звуках
    """
    sounds = Voices.objects.all()
    return render(request, 'home.html', {'sounds': sounds})

@login_required
def sound_library(request):
    """
    Страница библиотеки звуков касаток
    """
    sounds = Voices.objects.all()
    listened_ids = list(UserSound.objects.filter(user=request.user).values_list('sound_id', flat=True))
    if request.method == 'POST' and 'sound_id' in request.POST:
        # Записываем уникальное прослушивание звука
        AchievementService.record_sound_listened(request.user, sound_id=request.POST['sound_id'])
        return JsonResponse({'status': 'success'})
    return render(request, 'sound_library.html', {'sounds': sounds, 'listened_ids': listened_ids})

def about(request):
    """
    Страница 'О касатках'
    """
    return render(request, 'about.html')

def tests(request):
    """
    Страница с тестами о касатках
    """
    tests = Test.objects.all()
    user_progress = {}
    if request.user.is_authenticated:
        user_games = Game.objects.filter(user=request.user)
        for game in user_games:
            user_progress[game.name] = game.percent
    tests_with_progress = []
    for test in tests:
        percent = user_progress.get(test.name)
        tests_with_progress.append({'test': test, 'percent': percent})
    return render(request, 'tests.html', {'tests_with_progress': tests_with_progress})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    """Профиль пользователя с достижениями и прогрессом"""
    games = Game.objects.filter(user=request.user).order_by('-created_at')
    completed_tests = games.count()
    
    # Получаем прогресс и достижения пользователя
    progress = AchievementService.get_user_progress(request.user)
    achievements = AchievementService.get_user_achievements(request.user)
    
    context = {
        'games': games,
        'progress': progress,
        'achievements': achievements,
        'completed_tests': completed_tests,
    }
    return render(request, 'profile.html', context)

@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, test_id=test_id)
    questions = test.question_set.all().order_by('questiontest__order')
    if not questions.exists():
        return render(request, 'take_test.html', {'test': test, 'no_questions': True})

    total_questions = questions.count()
    q_idx = int(request.session.get(f'test_{test_id}_q_idx', 0))
    correct = int(request.session.get(f'test_{test_id}_correct', 0))
    answers_given = request.session.get(f'test_{test_id}_answers', [])
    if not isinstance(answers_given, list):
        answers_given = []

    if request.method == 'POST':
        answer_id = request.POST.get('answer')
        if answer_id:
            answer = Answer.objects.filter(id=answer_id, question=questions[q_idx]).first()
            answers_given.append(int(answer_id))
            if answer and answer.is_correct:
                correct += 1
            q_idx += 1
            request.session[f'test_{test_id}_q_idx'] = q_idx
            request.session[f'test_{test_id}_correct'] = correct
            request.session[f'test_{test_id}_answers'] = answers_given
        return HttpResponseRedirect(reverse('take_test', args=[test_id]))

    if q_idx >= total_questions:
        percent = int(100 * correct / total_questions) if total_questions else 0
        game, created = Game.objects.get_or_create(name=test.name, user=request.user)
        game.percent = percent
        game.save()
        
        # Записываем завершение теста и обновляем прогресс
        AchievementService.record_test_completed(request.user, correct, total_questions)
        
        result = {
            'correct': correct,
            'total': total_questions,
            'percent': percent
        }
        for key in [f'test_{test_id}_q_idx', f'test_{test_id}_correct', f'test_{test_id}_answers']:
            if key in request.session:
                del request.session[key]
        return render(request, 'take_test.html', {'test': test, 'result': result})

    question = questions[q_idx]
    return render(request, 'take_test.html', {'test': test, 'questions': [question], 'q_idx': q_idx+1, 'total_questions': total_questions})

@login_required
def achievements(request):
    """Страница достижений пользователя"""
    achievements = AchievementService.get_user_achievements(request.user)
    progress = AchievementService.get_user_progress(request.user)
    return render(request, 'achievements.html', {
        'achievements': achievements,
        'progress': progress
    })
