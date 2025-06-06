from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import mark_safe
from .models import Voices, Game, Test, Question, Answer, QuestionTest

User = get_user_model()


# --- Voice ---
@admin.register(Voices)
class VoicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'voice_preview')
    search_fields = ('name',)

    def voice_preview(self, obj):
        if obj.file:
            return mark_safe(f'<audio controls><source src="{obj.file.url}"></audio>')
        return "Нет аудио"
    voice_preview.short_description = 'Превью'


# --- Game ---
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_select_related = ('user',)
    search_fields = ('name', 'user__username')
    date_hierarchy = 'created_at'


# --- QuestionTest Inline ---
class QuestionTestInline(admin.TabularInline):
    model = QuestionTest
    extra = 1
    autocomplete_fields = ('question',)
    fields = ('question', 'order')  # добавлен порядок


# --- Test ---
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'name', 'question_count')
    search_fields = ('name',)
    list_display_links = ('test_id', 'name')
    inlines = [QuestionTestInline]

    def question_count(self, obj):
        return obj.questiontest_set.count()
    question_count.short_description = 'Вопросов'


# --- Answer Inline ---
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ('text', 'is_correct')
    show_change_link = True


# --- Question ---
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'image_preview', 'voice_link', 'test_list')
    list_filter = ('voice', 'questiontest__test')
    search_fields = ('text',)
    inlines = [AnswerInline, QuestionTestInline]

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет изображения"
    image_preview.short_description = 'Изображение'

    def voice_link(self, obj):
        if obj.voice and obj.voice.file:
            return mark_safe(f'<a href="{obj.voice.file.url}">Аудио</a>')
        return "Нет аудио"
    voice_link.short_description = 'Аудиофайл'

    def test_list(self, obj):
        return ", ".join([t.name for t in obj.tests.all()])
    test_list.short_description = 'Тесты'


# --- QuestionTest ---
@admin.register(QuestionTest)
class QuestionTestAdmin(admin.ModelAdmin):
    list_display = ('test', 'question', 'order')
    list_filter = ('test',)
    search_fields = ('question__text', 'test__name')
    autocomplete_fields = ('test', 'question')
    list_editable = ('order',)