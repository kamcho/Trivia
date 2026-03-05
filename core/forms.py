from django import forms
from .models import Schools, Teams
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolForm(forms.ModelForm):
    class Meta:
        model = Schools
        fields = ['name', 'address', 'city', 'country', 'phone', 'secondary_phone', 'email', 'website', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'secondary_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secondary Phone (Optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website URL (Optional)'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Teams
        fields = ['name', 'school', 'members', 'captain', 'patron']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Team Name'}),
            'school': forms.Select(attrs={'class': 'form-input'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-input min-h-[150px]'}),
            'captain': forms.Select(attrs={'class': 'form-input'}),
            'patron': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if school:
            self.fields['school'].initial = school
            self.fields['school'].queryset = Schools.objects.filter(pk=school.pk)
            # Filter users by school and student role
            self.fields['members'].queryset = User.objects.filter(school=school, role='student')
            self.fields['captain'].queryset = User.objects.filter(school=school, role='student')
        
        if user:
            self.fields['patron'].initial = user
            self.fields['patron'].queryset = User.objects.filter(pk=user.pk)
