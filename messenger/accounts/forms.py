from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from accounts.tools import tools
from .models import Profile


class RegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'loginInput',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'passwordInput',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'passwordInput',
    }))

    class Meta:
        model = User
        fields = {'username', 'password'}

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            tools.change_widget_attrs_class_to_invalid(self, 'username')
            user = User.objects.get(username=username)
            raise ValidationError('Имя пользователя занято')
        except User.DoesNotExist:
            tools.change_widget_attrs_class_to_valid(self, 'username')
            return username

    def clean_password(self):
        password = self.cleaned_data['password']
        password2 = self.data['password2']
        if password != password2:
            tools.change_widget_attrs_class_to_invalid(self, 'password')
            tools.change_widget_attrs_class_to_invalid(self, 'password2')
            raise ValidationError('Пароли не совпадают')
        return password


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'loginInput',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'passwordInput',
    }))

    fields = {'username', 'password'}

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            tools.change_widget_attrs_class_to_valid(self, 'username')
        except User.DoesNotExist:
            tools.change_widget_attrs_class_to_invalid(self, 'username')
            raise ValidationError('Пользователя не существует')
        return username

    def clean_password(self):
        username = self.data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            tools.change_widget_attrs_class_to_invalid(self, 'password')
            raise ValidationError('Пароль не верный')
        return password


class EditUserNames(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
    }))

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name


class EditUserPhoto(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo',)
