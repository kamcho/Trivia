from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import MyUser

class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=50,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = MyUser
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Email Address'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

class MyAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': True, 'placeholder': 'Email'})

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200',
                'placeholder': 'Enter your email address'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200'
            }),
           
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition duration-200'
            })


class QuickUserCreationForm(forms.ModelForm):
    """Quick user creation form for group member management"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500',
            'placeholder': 'Enter email address'
        })
    )
    role = forms.ChoiceField(
        choices=MyUser.ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500'
        })
    )
    
    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email', 'role']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set a temporary password - user will need to reset it
        user.set_password('TempPass123!')
        user.username = user.email  # Use email as username
        if commit:
            user.save()
        return user