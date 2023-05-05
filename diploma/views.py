import binascii
import json
import random
import hashlib
import uuid

import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from account.models import Confirmation, UserInfo
from store.cart_handler import Cart
from store.forms import CaptchaAuthenticationForm
from store.models import Order, Category

from django.shortcuts import render, redirect

from . import settings
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages


def main(request):
    items = list(Category.objects.all())
    random_items = random.sample(items, 4)
    print(request.META.get('HTTP_REFERER'))
    print(request.META.get('HTTP_REFERER'))
    return render(
        request,
        'main.html',
        context={"random_items": random_items},
    )


def page_not_found_view(request, exception='re'):
    return render(request, '404.html', status=404)


"""
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            user_confirmation = Confirmation(user=user).save()
            print()

            login(request, user)
            return redirect("index")
        else:
            print(form.errors.as_data())
            for error in list(form.errors.values()):
                print(error)
                messages.error(request, error)
    else:
        form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})
"""


def ajax_update(request):
    orders_count = Order.objects.filter(status__icontains="created").count()

    cart_hex = request.session.get('cart')
    cart = Cart()
    cart.hex_decode(cart_hex)

    response = {
        'orders_count': orders_count,
        'cart_count': cart.get_size()
    }
    return JsonResponse(response)


def get_user_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def login_view(request):
    if request.method == "POST":
        form = CaptchaAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                userinfo = get_object_or_404(UserInfo, user=user)
                print(userinfo)
            except Exception as ex:
                print(ex)
                userinfo = UserInfo(user=user, is_confirmed=True)
                userinfo.save()
            if userinfo.user.is_active:
                login(request, user)
            return redirect("/")

    else:
        form = CaptchaAuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# NOTIFICATION ABOUT PAYMENT
@csrf_exempt
def success(request):
    try:
        confirmation_string = "{}&{}&{}&{}&{}&{}&{}&{}&{}".format(request.POST.get("notification_type"),
                                                                  request.POST.get("operation_id"),
                                                                  request.POST.get("amount"),
                                                                  request.POST.get("currency"),
                                                                  request.POST.get("datetime"),
                                                                  request.POST.get("sender"),
                                                                  request.POST.get("codepro"),
                                                                  settings.YOOMONEY_VERIFICATION_CODE,
                                                                  request.POST.get("label"))
        byte_string = str.encode(confirmation_string)
        hash_object = hashlib.sha1(byte_string)
        hex_dig = hash_object.hexdigest()
        # Проверка на подлиность запроса
        if hex_dig == request.POST.get("sha1_hash"):
            label = request.POST.get("label")
            if label:
                order = get_object_or_404(Order, pk=label)
                order.status = "PAYED"
                order.modification_date_time = timezone.now
                order.save()
        else:
            raise Exception("PAYMENT VERIFICATION ERROR!")
    except Exception as ex:
        print(ex)

    return HttpResponse(status=200)
