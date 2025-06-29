# Generated by Django 5.2.1 on 2025-06-16 08:59

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_game_percent'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название достижения')),
                ('description', models.TextField(verbose_name='Описание')),
                ('icon', models.ImageField(upload_to='achievements/', verbose_name='Иконка')),
                ('type', models.CharField(choices=[('sound', 'Звуки'), ('dialect', 'Диалекты'), ('population', 'Популяции'), ('test', 'Тесты')], max_length=20, verbose_name='Тип достижения')),
                ('requirement', models.IntegerField(default=1, verbose_name='Требуемое количество')),
                ('xp_reward', models.IntegerField(default=100, verbose_name='Награда в XP')),
            ],
            options={
                'verbose_name': 'Достижение',
                'verbose_name_plural': 'Достижения',
            },
        ),
        migrations.CreateModel(
            name='UserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'Наблюдатель'), (2, 'Любитель'), (3, 'Исследователь'), (4, 'Биолог'), (5, 'Эксперт по китообразным'), (6, 'Мастер-китолог')], default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(6)])),
                ('xp', models.IntegerField(default=0)),
                ('sounds_listened', models.IntegerField(default=0)),
                ('tests_completed', models.IntegerField(default=0)),
                ('correct_answers', models.IntegerField(default=0)),
                ('facts_learned', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Прогресс пользователя',
                'verbose_name_plural': 'Прогресс пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_earned', models.DateTimeField(auto_now_add=True)),
                ('progress', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Достижение пользователя',
                'verbose_name_plural': 'Достижения пользователей',
                'unique_together': {('user', 'achievement')},
            },
        ),
    ]
