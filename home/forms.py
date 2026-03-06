from django import forms
from .models import Cohort, TriviaMode, Question, QuestionOption, QuestionImage, Tests

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = ['name', 'description', 'start_date', 'end_date', 'status', 'is_open']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TriviaModeForm(forms.ModelForm):
    class Meta:
        model = TriviaMode
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'difficulty', 'score', 'time', 'min_age', 'max_age', 'min_grade', 'max_grade', 'explanation', 'metadata']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'time': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10'}),
            'max_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 18'}),
            'min_grade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4'}),
            'max_grade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Explanation shown to students after answering'}),
            'metadata': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional JSON metadata'}),
        }

class QuestionImageForm(forms.ModelForm):
    class Meta:
        model = QuestionImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }

class TestForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['name', 'description', 'difficulty', 'mode', 'questions', 'time', 'min_age', 'max_age', 'min_grade', 'max_grade', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'mode': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'questions': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'time': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10'}),
            'max_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 18'}),
            'min_grade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4'}),
            'max_grade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['question', 'option_text', 'is_correct']
        widgets = {
            'question': forms.Select(attrs={'class': 'form-control'}),
            'option_text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
