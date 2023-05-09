from django.db.models.signals import pre_delete, post_save, pre_save, post_init, pre_init
from django.dispatch import receiver
from django.utils import timezone
from store.models import Product, Order


@receiver(pre_delete, sender=Product)
def delete_image(sender, instance, **kwargs):
    instance.image.delete(save=False)


@receiver(pre_save, sender=Order)
def save_order(sender, instance, **kwargs):
    instance.modification_date_time = timezone.now()
