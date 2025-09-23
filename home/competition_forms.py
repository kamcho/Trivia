from django import forms
from .models import ActivityCategory, CompetitionActivity, Competition


class ActivityCategoryForm(forms.ModelForm):
    class Meta:
        model = ActivityCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter activity category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter a brief description',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class CompetitionActivityForm(forms.ModelForm):
    class Meta:
        model = CompetitionActivity
        fields = ['name', 'description', 'metadata', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter activity name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter activity description',
                'rows': 3
            }),
            'metadata': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200 font-mono',
                'placeholder': 'Enter JSON metadata (if any)',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = [
            'name', 'description', 'activities', 'start_date', 'end_date', 
            'metadata', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter competition name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'placeholder': 'Enter competition description',
                'rows': 3
            }),
            'activities': forms.SelectMultiple(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
                'style': 'height: auto; min-height: 100px;'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
            }),
            'metadata': forms.Textarea(attrs={
                'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200 font-mono',
                'placeholder': 'Enter JSON metadata (if any)',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-700/50 bg-slate-900/60 text-indigo-600'
            }),
        }
