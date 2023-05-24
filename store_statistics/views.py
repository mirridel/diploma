from datetime import timedelta, datetime

from django.db.models import Q, Max, Avg, Min
from django.shortcuts import render, redirect
from django.utils import timezone

from store.models import Order
from store.templatetags.has_group import has_group


def index(request):
    if not has_group(request.user, "admin"):
        return redirect("index")

    # ДО КАКОГО ЧИСЛА
    if request.GET.get("end"):
        end_date = datetime.strptime(request.GET.get("end"), '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    # С КАКОГО ЧИСЛА
    if request.GET.get("start"):
        start_date = datetime.strptime(request.GET.get("start"), '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
    # ДАТЫ ДЛЯ СТАТИСТИКИ
    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    all_orders_count = list()
    payed_orders_count = list()
    context = dict()

    if request.GET.get('spec_name') and request.GET.get('spec_val'):
        spec_name = request.GET.get('spec_name')
        spec_val = request.GET.get('spec_val')
        context["spec_name"] = spec_name
        context["spec_val"] = spec_val
        for date in dates:
            query = Order.objects.filter(Q(creation_date_time__date=date) &
                                         Q(shoppingcart__product__specs__name__icontains=spec_name) &
                                         Q(shoppingcart__product__specs__val__icontains=spec_val))
            all_orders_count.append(query.count())
            payed_query = query.filter(status="PAYED")
            payed_orders_count.append(payed_query.count())

    if not all_orders_count:
        for date in dates:
            query = Order.objects.filter(creation_date_time__date=date)
            all_orders_count.append(query.count())
            payed_query = query.filter(status="PAYED")
            payed_orders_count.append(payed_query.count())

    table = list()
    for i in range(0, len(dates)):
        table.append({"date": dates[i],
                      "all_orders_count": all_orders_count[i],
                      "payed_orders_count": payed_orders_count[i]})

    query = Order.objects.filter(creation_date_time__range=(start_date, end_date))
    context["min"] = query.aggregate(Min('total'))["total__min"]  # {'total__min': *}
    context["avg"] = query.aggregate(Avg('total'))["total__avg"]  # {'total__avg': *}
    context["max"] = query.aggregate(Max('total'))["total__max"]  # {'total__max': *}
    context["end_date"] = end_date
    context["start_date"] = start_date
    context['table'] = table
    context["orders_count"] = Order.objects.all().count()
    context["data"] = all_orders_count
    context["payed_data"] = payed_orders_count
    context["labels"] = [item.__str__() for item in dates]

    return render(request, "store_statistics/index.html", context=context)
