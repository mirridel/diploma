from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from diploma import settings


class CaptchaAuthenticationForm(AuthenticationForm):
    recaptcha = ReCaptchaField(widget=ReCaptchaV3(attrs={
        'required_score': 0.85
    }), public_key=settings.RECAPTCHA_PUBLIC_KEY,
        private_key=settings.RECAPTCHA_PRIVATE_KEY,
        label=False)


class CaptchaRegistrationForm(UserCreationForm):
    recaptcha = ReCaptchaField(widget=ReCaptchaV3(attrs={
        'required_score': 0.85
    }), public_key=settings.RECAPTCHA_PUBLIC_KEY,
        private_key=settings.RECAPTCHA_PRIVATE_KEY,
        label=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        try:
            user = super(CaptchaRegistrationForm, self).save(commit=False)
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
            return user
        except Exception as ex:
            print(ex)
            return False


class PersonalInformationForm(forms.Form):
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(label='Телефон', required=False)
