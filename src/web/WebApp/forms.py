from django import forms
from .models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    location = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'grade', 'pronouns', 'password', 'school']


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class UserEditForm(forms.ModelForm):
    # Create a form to change the attributes of the User model
    class Meta:
        model = User
        # TODO: Add school validator
        fields = ['username', 'email', 'first_name', 'last_name', 'grade', 'pronouns', 'school']