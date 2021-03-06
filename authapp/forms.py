from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from authapp.models import Gamer
from django import forms


class GamerLoginForm(AuthenticationForm):
    class Meta:
        model = Gamer
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class GamerRegisterForm(UserCreationForm):
    class Meta:
        model = Gamer
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'gender', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''


class GamerEditForm(UserChangeForm):
    class Meta:
        model = Gamer
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'avatar', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
            if field_name == 'password':
                field.widget = forms.HiddenInput()
