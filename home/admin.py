from django.contrib import admin
from .models import Cohort, TriviaMode, Question, QuestionOption, QuestionImage, Tests, TestSession, TestResponses

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4

class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'difficulty', 'score', 'time')
    list_filter = ('difficulty', 'question_type')
    inlines = [QuestionOptionInline, QuestionImageInline]

@admin.register(Tests)
class TestsAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'is_active', 'time')
    filter_horizontal = ('mode', 'questions')

class TestResponsesInline(admin.TabularInline):
    model = TestResponses
    extra = 0

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('test', 'user', 'team', 'score', 'start_time')
    inlines = [TestResponsesInline]

admin.site.register(Cohort)
admin.site.register(TriviaMode)
admin.site.register(TestResponses)
