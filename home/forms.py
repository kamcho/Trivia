from django import forms
from .models import (
    Church, TriviaGroup, QuestionCategory, Question, Choice,
    ActivityCategory, CompetitionActivity, Competition, Cohort, TestQuiz,
    ActivityInstruction, ActivityRule, CompetitionRegistrationWindow, CompetitionScheduleItem
)


class ChurchForm(forms.ModelForm):
    class Meta:
        model = Church
        fields = [
            'name', 'category', 'address', 'city', 'location', 'country',
            'contact_email', 'phone_number', 'website', 'logo', 'established_year',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200', 'placeholder': 'Church name'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'}),
            'address': forms.TextInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200', 'placeholder': 'Street, address'}),
            'city': forms.TextInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'}),
            'location': forms.TextInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200', 'placeholder': 'Neighborhood/Region'}),
            'country': forms.TextInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'}),
            'website': forms.URLInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'}),
            'logo': forms.FileInput(attrs={'class': 'hidden', 'id': 'logo-upload'}),
            'established_year': forms.NumberInput(attrs={'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct', 'explanation']
        widgets = {
            'choice_text': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter choice text'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Optional explanation for this choice',
                'rows': 3
            }),
        }

class TriviaGroupForm(forms.ModelForm):
    class Meta:
        model = TriviaGroup
        fields = [
            'name', 'church', 'category', 'description', 'patron', 'captain', 
            'max_members', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Group name'
            }),
            'church': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Describe your trivia group...',
                'rows': 4
            }),
            'patron': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'captain': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'max_members': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 1,
                'max': 20
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class QuestionCategoryForm(forms.ModelForm):
    class Meta:
        model = QuestionCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Category name (e.g., Old Testament, New Testament)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Describe this question category...',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'categories', 'level', 'question_text', 'difficulty', 'question_type',
            'explanation', 'bible_reference', 'points', 'penalty', 'is_active'
        ]
        widgets = {
            'categories': forms.SelectMultiple(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'size': 6
            }),
            'level': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'question_text': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter your trivia question...',
                'rows': 4
            }),
            'level': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'question_type': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Optional explanation for the correct answer...',
                'rows': 3
            }),
            'bible_reference': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'e.g., John 3:16, Genesis 1:1'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 1,
                'max': 10
            }),
            'penalty': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 0,
                'max': 10
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class ActivityCategoryForm(forms.ModelForm):
    class Meta:
        model = ActivityCategory
        fields = ['name', 'slug', 'description', 'is_active']
        widgets = {
            'name': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Unique identifier (e.g., youth-games)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Describe this activity category...',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class CompetitionActivityForm(forms.ModelForm):
    class Meta:
        model = CompetitionActivity
        fields = ['name', 'categories', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Competition activity name'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Describe this competition activity...',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class ActivityInstructionForm(forms.ModelForm):
    class Meta:
        model = ActivityInstruction
        fields = ['content', 'order', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'rows': 2,
                'placeholder': 'Instruction text'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-24 rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class ActivityRuleForm(forms.ModelForm):
    class Meta:
        model = ActivityRule
        fields = ['content', 'order', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'rows': 2,
                'placeholder': 'Rule text'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-24 rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'description', 'activities', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Competition name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Describe this competition...',
                'rows': 4
            }),
            'activities': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class TestQuizForm(forms.ModelForm):
    class Meta:
        model = TestQuiz
        fields = [
            'name', 'description', 'level', 'participation', 'difficulty', 'quiz_type', 'questions',
            'time_limit', 'max_attempts', 'passing_score', 'is_active',
            'is_public', 'requires_authentication', 'instructions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Quiz name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Quiz description',
                'rows': 3
            }),
            'difficulty': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'participation': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'quiz_type': forms.Select(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
            }),
            'questions': forms.SelectMultiple(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'size': 10
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Time limit in minutes (optional)',
                'min': 1
            }),
            'max_attempts': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 1
            }),
            'passing_score': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'min': 0,
                'max': 100
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
            'requires_authentication': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Instructions for taking this quiz',
                'rows': 4
            }),
        }


class CompetitionRegistrationWindowForm(forms.ModelForm):
    opens_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    closes_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    class Meta:
        model = CompetitionRegistrationWindow
        fields = ['competition', 'opens_at', 'closes_at', 'capacity', 'fee_amount', 'fee_currency', 'terms_url', 'notes', 'is_active']
        widgets = {
            'competition': forms.Select(attrs={'class': 'vTextField'}),
        }


class CompetitionScheduleItemForm(forms.ModelForm):
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    class Meta:
        model = CompetitionScheduleItem
        fields = ['competition', 'title', 'description', 'start_at', 'end_at', 'location_hint', 'order', 'is_public']
        widgets = {}
