from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV3
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from diploma import settings
from store.models import Product, Specs, Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['client', "creation_date_time", "modification_date_time", "status", "total"]
        widgets = {
            'phone': forms.TextInput()
        }


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        initial = self.instance.category
        print("initial {}".format(initial))
        self.fields['category'].initial = initial
        self.fields['image'].required = False


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)
        print(self.instance)
        self.fields['image'].required = False


class AddSpecsForm(forms.ModelForm):
    class Meta:
        model = Specs
        fields = "__all__"
        widgets = {
            'product': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(AddSpecsForm, self).__init__(*args, **kwargs)
        initial = self.instance.product
        self.fields['product'].initial = initial


class CaptchaAuthenticationForm(AuthenticationForm):
    recaptcha = ReCaptchaField(widget=ReCaptchaV3(attrs={
        'required_score': 0.85
    }), public_key=settings.RECAPTCHA_PUBLIC_KEY,
        private_key=settings.RECAPTCHA_PRIVATE_KEY,
        label=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'modification_date_time': forms.HiddenInput()
        }
