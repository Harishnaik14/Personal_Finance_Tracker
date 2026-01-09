from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re
from django.core.exceptions import ValidationError

def validate_username_custom(username):
    if not 4 <= len(username) <= 12:
        raise ValidationError("Username must be between 4 and 12 characters long.")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores (_).")
    return username

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="A valid email address is required for registration.")
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return validate_username_custom(username)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'currency', 'opening_balance']
        labels = {
            'currency': 'Region / Currency',
            'opening_balance': 'Opening Balance',
        }
        help_texts = {
            'opening_balance': 'Set your starting balance (what you had before using this app)',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return validate_username_custom(username)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is used by another user (excluding current user)
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email
