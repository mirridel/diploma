import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Confirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    _uuid = models.UUIDField(default=uuid.uuid4())

    class Meta:
        verbose_name_plural = "Для верификации"

    @property
    def uuid(self):
        return self._uuid


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+7\d{10}$', message="Номер телефона должен быть в формате: '+7xxxxxxxxxx'.")
    phone = models.CharField(validators=[phone_regex], verbose_name="Телефон", max_length=32, default="")
    # address = None
    # image = None
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Расширение для пользователя"
