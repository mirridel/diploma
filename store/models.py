from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models

from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(verbose_name="Название", max_length=128)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product-list', args=[str(self.id)])

    class Meta:
        verbose_name_plural = "Категории"


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Название",
                             max_length=32)
    image = models.ImageField(verbose_name="Изображение",
                              upload_to='uploads/',
                              null=True,
                              blank=True)
    price = models.PositiveIntegerField(verbose_name="Цена")
    warranty = models.PositiveIntegerField(verbose_name="Гарантия")
    description = models.TextField(verbose_name="Описание",
                                   blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    def get_absolute_url(self):
        return reverse('store:product-detail', args=[str(self.id)])

    class Meta:
        verbose_name_plural = "Товары"

    def __str__(self):
        return "({}) {} : {} : {}".format(self.id, self.category, self.title, self.price)


class Specs(models.Model):
    class Meta:
        verbose_name_plural = "Характеристики"

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Название", max_length=128)
    description = models.CharField(verbose_name="Описание", default="", max_length=128)
    val = models.CharField(verbose_name="Значение", default="", max_length=128)

    # Возвращаем ссылку на продукт
    def get_absolute_url(self):
        return reverse('store:product-detail', args=[str(self.product.id)])

    def __str__(self):
        return "({}) {} : {}".format(self.product, self.name, self.val if self.val else "Пусто")


class Order(models.Model):
    order_statuses = [
        ('CREATED', 'Создан'),
        ('PAYED', 'Оплачен'),
        ('CONFIRMED', 'Подтвержден'),
        ('CLOSED', 'Закрыт'),
        ('CANCELLED', 'Отменен'),
        ('DELETED', 'Удален')
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
    # FOR CLIENT
    first_name = models.CharField(max_length=255, verbose_name="Имя", default="")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия", default="")
    phone_regex = RegexValidator(regex=r'^\+7\d{10}$', message="Номер телефона должен быть в формате: '+7xxxxxxxxxx'.")
    phone = models.CharField(validators=[phone_regex], verbose_name="Телефон", max_length=32, default="")
    address = models.CharField(max_length=255, verbose_name="Адрес", default="")
    message = models.TextField(blank=True, verbose_name="Сообщение", default="")
    total = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    # FOR SELLER
    creation_date_time = models.DateTimeField(default=timezone.now)
    modification_date_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=order_statuses, max_length=128)

    def get_absolute_url(self):
        return reverse('store:order-detail', args=[str(self.id)])

    def get_status(self):
        return dict(Order.order_statuses)[self.status]

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return "({}) {}".format(self.id, self.get_status())


class ShoppingCart(models.Model):
    order = models.ForeignKey(Order, verbose_name="Заказ", on_delete=models.CASCADE, default=None)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Количество")
    price = models.IntegerField(verbose_name="Цена",
                                null=True)

    class Meta:
        verbose_name = "Состав заказа"
        verbose_name_plural = "Состав заказа"

    def __str__(self):
        return "({}) ({}) : {} : {}".format(self.order.id, self.product, self.quantity, self.price)
