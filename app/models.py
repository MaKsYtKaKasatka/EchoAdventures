from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe


class Voices(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='voices/')

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Добавлено поле

    def __str__(self):
        return self.name


class Test(models.Model):
    test_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    voice = models.ForeignKey(Voices, on_delete=models.SET_NULL, null=True, blank=True)
    tests = models.ManyToManyField(Test, through='QuestionTest')

    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text

    def image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="100" />')
        return "Нет изображения"

    image_preview.short_description = 'Изображение'


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False)  # Опционально

    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text


class QuestionTest(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        to_field='test_id',
        db_column='test_id'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

class Meta:
        db_table = 'app_questiontest'  # изменено на уникальное имя
        ordering = ['order']
        verbose_name = 'Связь вопроса и теста'
        verbose_name_plural = 'Связи вопросов и тестов'

def __str__(self):
    return f"{self.test} - {self.question}"