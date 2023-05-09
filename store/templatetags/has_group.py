from django import template
from django.contrib.auth.models import Group
from django.http import request

from store.cart_handler import Cart

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False
    return group in user.groups.all()


@register.filter(name='in_cart')
def in_cart(product, cart_hex):
    cart = Cart()
    cart.hex_decode(cart_hex)
    return cart.is_exist(product.id)
