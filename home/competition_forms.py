from django import forms
from .models import ActivityCategory, CompetitionActivity, Competition, TriviaGroup
from django.db import models


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


class CompetitionBookingForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=TriviaGroup.objects.none(),
        required=False,
        label='Group (optional)',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
        })
    )
    num_slots = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Number of slots',
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
            'placeholder': '1'
        })
    )
    phone_number = forms.CharField(
        required=False,
        label='Phone number (for M-Pesa receipts)',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200',
            'placeholder': 'e.g. 07xxxxxxxx'
        })
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('mpesa', 'M-Pesa'),
            ('paypal_card', 'PayPal/Card'),
            ('none', 'None'),
        ],
        initial='none',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit group choices to groups the user can represent
        qs = TriviaGroup.objects.none()
        if user and getattr(user, 'is_authenticated', False):
            qs = TriviaGroup.objects.filter(
                models.Q(members=user) | models.Q(captain=user) | models.Q(patron=user)
            ).distinct().order_by('church__name', 'name')
        self.fields['group'].queryset = qs
        # If user has no groups, make field not required and with an empty option
        self.fields['group'].required = False

    def clean(self):
        cleaned = super().clean()
        payment_method = cleaned.get('payment_method')
        phone = (cleaned.get('phone_number') or '').strip()
        if payment_method == 'mpesa' and not phone:
            self.add_error('phone_number', 'Phone number is required for M-Pesa payments.')
        return cleaned
