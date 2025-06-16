from django.db import transaction
from django.db.models import Count
from .django_models import Achievement, UserAchievement, UserProgress, UserSound

class AchievementService:
    @staticmethod
    def check_achievements(user):
        """Проверяет и обновляет достижения пользователя"""
        progress = UserProgress.objects.get_or_create(user=user)[0]
        
        # Проверяем достижения за прослушивание звуков
        sounds_count = progress.sounds_listened
        sound_achievements = Achievement.objects.filter(type='sound')
        for achievement in sound_achievements:
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
                defaults={'progress': 0}
            )
            if not created and user_achievement.progress < achievement.requirement:
                user_achievement.progress = min(sounds_count, achievement.requirement)
                user_achievement.save()
                if user_achievement.progress >= achievement.requirement:
                    progress.add_xp(achievement.xp_reward)

        # Проверяем достижения за тесты
        tests_completed = progress.tests_completed
        test_achievements = Achievement.objects.filter(type='test')
        for achievement in test_achievements:
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
                defaults={'progress': 0}
            )
            if not created and user_achievement.progress < achievement.requirement:
                user_achievement.progress = min(tests_completed, achievement.requirement)
                user_achievement.save()
                if user_achievement.progress >= achievement.requirement:
                    progress.add_xp(achievement.xp_reward)

    @staticmethod
    def record_sound_listened(user, sound_id=None):
        """Записывает уникальное прослушивание звука и обновляет прогресс"""
        with transaction.atomic():
            if sound_id is not None:
                # Проверяем, слушал ли пользователь этот звук
                if not UserSound.objects.filter(user=user, sound_id=sound_id).exists():
                    UserSound.objects.create(user=user, sound_id=sound_id)
                    progress = UserProgress.objects.get_or_create(user=user)[0]
                    progress.sounds_listened = UserSound.objects.filter(user=user).count()
                    progress.add_xp(10)  # 10 XP за уникальное прослушивание
                    progress.save()
                    AchievementService.check_achievements(user)
            else:
                # Старый режим (без конкретного звука)
                progress = UserProgress.objects.get_or_create(user=user)[0]
                progress.sounds_listened += 1
                progress.add_xp(10)
                progress.save()
                AchievementService.check_achievements(user)

    @staticmethod
    def record_test_completed(user, correct_answers, total_questions):
        """Записывает завершение теста и обновляет прогресс"""
        with transaction.atomic():
            progress = UserProgress.objects.get_or_create(user=user)[0]
            progress.tests_completed += 1
            progress.correct_answers += correct_answers
            
            # Начисляем XP за тест
            base_xp = 50  # Базовый XP за завершение теста
            correct_answers_xp = (correct_answers / total_questions) * 100  # Дополнительный XP за правильные ответы
            total_xp = base_xp + correct_answers_xp
            
            progress.add_xp(int(total_xp))
            progress.save()
            AchievementService.check_achievements(user)

    @staticmethod
    def get_user_achievements(user):
        """Возвращает все достижения пользователя с прогрессом"""
        achievements = Achievement.objects.all()
        user_achievements = UserAchievement.objects.filter(user=user)
        user_achievements_dict = {ua.achievement_id: ua for ua in user_achievements}
        
        result = []
        for achievement in achievements:
            user_achievement = user_achievements_dict.get(achievement.id)
            progress_value = user_achievement.progress if user_achievement else 0
            percent = int(100 * progress_value / achievement.requirement) if achievement.requirement else 0
            result.append({
                'achievement': achievement,
                'progress': progress_value,
                'percent': percent,
                'completed': user_achievement is not None and progress_value >= achievement.requirement,
                'date_earned': user_achievement.date_earned if user_achievement else None
            })
        return result

    @staticmethod
    def get_user_progress(user):
        """Возвращает прогресс пользователя"""
        progress = UserProgress.objects.get_or_create(user=user)[0]
        return {
            'level': progress.level,
            'level_name': dict(UserProgress.LEVELS)[progress.level],
            'xp': progress.xp,
            'next_level_xp': progress.next_level_xp,
            'progress_percentage': progress.progress_percentage,
            'sounds_listened': progress.sounds_listened,
            'tests_completed': progress.tests_completed,
            'correct_answers': progress.correct_answers,
            'facts_learned': progress.facts_learned
        } 