from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Achievement(models.Model):
    """Модель для достижений"""
    ACHIEVEMENT_TYPES = [
        ('sound', 'Звуки'),
        ('dialect', 'Диалекты'),
        ('population', 'Популяции'),
        ('test', 'Тесты'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название достижения")
    description = models.TextField(verbose_name="Описание")
    icon = models.ImageField(upload_to='achievements/', verbose_name="Иконка")
    type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, verbose_name="Тип достижения")
    requirement = models.IntegerField(default=1, verbose_name="Требуемое количество")
    xp_reward = models.IntegerField(default=100, verbose_name="Награда в XP")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

class UserAchievement(models.Model):
    """Модель для связи пользователя с достижениями"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('user', 'achievement')
        verbose_name = "Достижение пользователя"
        verbose_name_plural = "Достижения пользователей"

class UserProgress(models.Model):
    """Модель для отслеживания прогресса пользователя"""
    LEVELS = [
        (1, 'Наблюдатель'),
        (2, 'Любитель'),
        (3, 'Исследователь'),
        (4, 'Биолог'),
        (5, 'Эксперт по китообразным'),
        (6, 'Мастер-китолог'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    level = models.IntegerField(default=1, choices=LEVELS, validators=[MinValueValidator(1), MaxValueValidator(6)])
    xp = models.IntegerField(default=0)
    sounds_listened = models.IntegerField(default=0)
    tests_completed = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    facts_learned = models.IntegerField(default=0)

    @property
    def next_level_xp(self):
        """Возвращает количество XP, необходимое для следующего уровня"""
        return self.level * 1000

    @property
    def progress_percentage(self):
        """Возвращает процент прогресса до следующего уровня"""
        return min(100, (self.xp / self.next_level_xp) * 100)

    def add_xp(self, amount):
        """Добавляет XP и проверяет повышение уровня"""
        self.xp += amount
        while self.xp >= self.next_level_xp and self.level < 6:
            self.xp -= self.next_level_xp
            self.level += 1
        self.save()

    def __str__(self):
        return f"{self.user.username} - Уровень {self.level}"

    class Meta:
        verbose_name = "Прогресс пользователя"
        verbose_name_plural = "Прогресс пользователей"

class UserSound(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    sound = models.ForeignKey('Voices', on_delete=models.CASCADE)
    listened_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'sound') 