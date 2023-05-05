from django import template
from django.contrib.auth.models import Group
from django.http import request

from store.cart_handler import Cart

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='in_cart')
def in_cart(product, cart_hex):
    cart = Cart()
    cart.hex_decode(cart_hex)
    return cart.is_exist(product.id)
