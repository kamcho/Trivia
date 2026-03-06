from django.db import models
from django.conf import settings

# Create your models here.

class Cohort(models.Model):
    status_choices = [
        ('Onboarding', 'Onboarding'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_open = models.BooleanField(default=True)
    status = models.CharField(max_length=100, choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TriviaMode(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Question(models.Model):
    question_type_choices = [
        ('multiple choice', 'Multiple Choice'),
        ('open ended', 'OpenEnded'),
    ]
    difficulty_choices = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    question_type = models.CharField(max_length=100, choices=question_type_choices)
    question_text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=difficulty_choices, default='medium')
    explanation = models.TextField(blank=True, null=True, help_text='Explanation shown after answering')
    metadata = models.JSONField(null=True, blank=True)
    time = models.IntegerField()
    score = models.IntegerField()
    min_age = models.IntegerField(null=True, blank=True, help_text='Minimum recommended age')
    max_age = models.IntegerField(null=True, blank=True, help_text='Maximum recommended age')
    min_grade = models.IntegerField(null=True, blank=True, help_text='Minimum recommended grade')
    max_grade = models.IntegerField(null=True, blank=True, help_text='Maximum recommended grade')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=100)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.option_text


class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='question_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)
    def __str__(self):
        return f"Image for: {self.question.question_text[:50]}"


class Tests(models.Model):
    difficulty_choices = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=100, choices=difficulty_choices)
    name = models.CharField(max_length=100)
    mode = models.ManyToManyField(TriviaMode, related_name='modes')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    questions = models.ManyToManyField(Question, related_name='questions')
    time = models.IntegerField()
    min_age = models.IntegerField(null=True, blank=True, help_text='Minimum recommended age')
    max_age = models.IntegerField(null=True, blank=True, help_text='Maximum recommended age')
    min_grade = models.IntegerField(null=True, blank=True, help_text='Minimum recommended grade')
    max_grade = models.IntegerField(null=True, blank=True, help_text='Maximum recommended grade')  
    def __str__(self):
        return self.name

class TestSession(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey('core.Teams',null=True, blank=True, on_delete=models.CASCADE)   
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField()

    @property
    def duration_display(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "N/A"

    def __str__(self):
        return self.test.name

class TestResponses(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(QuestionOption,null=True, blank=True, on_delete=models.CASCADE)
    response = models.JSONField(null=True, blank=True)
    score = models.IntegerField()
    def __str__(self):
        return self.question.question_text