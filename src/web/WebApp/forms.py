from django import forms
from .models import User
from captcha.fields import CaptchaField
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    # Make the user bio field label above the text area
    user_bio = forms.CharField(widget=forms.Textarea(), label='Bio', label_suffix=':\n', required=False)
    captcha = CaptchaField(label_suffix=':\n')
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'grade', 'pronouns', 'password', 'school', 'user_bio']

class SchoolSelector(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SchoolSelector, self).__init__(*args, **kwargs)
        choices = [(i, i) for i in kwargs['schools']]
        self.fields['school'].choices = choices
    choices = []
    school = forms.ChoiceField(choices=choices)

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class UserEditForm(forms.ModelForm):
    user_bio = forms.CharField(widget=forms.Textarea(), label='Bio', label_suffix=':\n', required=False)
    class Meta:
        model = User
        # TODO: Add school validator
        fields = ['username', 'email', 'first_name', 'last_name', 'grade', 'pronouns', 'user_bio']
