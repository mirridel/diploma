from datetime import timedelta, datetime

from django.db.models import Q, Count, Max, Avg, Min
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from store.models import Order


def index(request):
    orders = Order.objects.all()

    context = dict()
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    orders_count = list()
    payed_orders_count = list()

    if request.POST:
        end_date = datetime.strptime(request.POST.get("end"), '%Y-%m-%d').date()
        start_date = datetime.strptime(request.POST.get("start"), '%Y-%m-%d').date()

        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        """
        orders_month = Order.objects.filter(
        creation_date_time__range=(start_date, end_date)).annotate(
        day=TruncDate('creation_date_time')).values('day').annotate(count=Count('id')).order_by('day')

        if request.POST.get('spec_name') and request.POST.get('spec_val'):
            orders_month = Order.objects.filter(
                Q(creation_date_time__range=(start_date, end_date)) &
                Q(shoppingcart__product__specs__name__icontains=request.POST.get('spec_name')) &
                Q(shoppingcart__product__specs__val__icontains=request.POST.get('spec_val'))).annotate(
                day=TruncDate('creation_date_time')).values('day').annotate(count=Count('id')).order_by('day')
        """

        if request.POST.get('spec_name') and request.POST.get('spec_val'):
            for date in dates:
                count = Order.objects.filter(Q(creation_date_time__date=date) &
                                             Q(shoppingcart__product__specs__name__icontains=request.POST.get('spec_name')) &
                                             Q(shoppingcart__product__specs__val__icontains=request.POST.get('spec_val'))).count()
                orders_count.append({'day': date, 'count': count})

            for date in dates:
                count = Order.objects.filter(Q(creation_date_time__date=date) &
                                             Q(shoppingcart__product__specs__name__icontains=request.POST.get(
                                                 'spec_name')) &
                                             Q(shoppingcart__product__specs__val__icontains=request.POST.get(
                                                 'spec_val')) &
                                             Q(status="PAYED")).count()
                payed_orders_count.append({'day': date, 'count': count})
        else:
            for date in dates:
                count = Order.objects.filter(creation_date_time__date=date).count()
                orders_count.append({'day': date, 'count': count})

            for date in dates:
                count = Order.objects.filter(Q(creation_date_time__date=date) &
                                             Q(status="PAYED")).count()
                payed_orders_count.append({'day': date, 'count': count})

    else:
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        for date in dates:
            count = Order.objects.filter(creation_date_time__date=date).count()
            orders_count.append({'day': date, 'count': count})

        for date in dates:
            count = Order.objects.filter(Q(creation_date_time__date=date) &
                                         Q(status="PAYED")).count()
            payed_orders_count.append({'day': date, 'count': count})
        """
        orders_month = Order.objects.filter(
            creation_date_time__range=(start_date, end_date)).annotate(
            day=TruncDate('creation_date_time')).values('day').annotate(count=Count('id')).order_by('-day')
        """

    query = Order.objects.filter(creation_date_time__range=(start_date, end_date))
    context["min"] = query.aggregate(Min('total'))["total__min"]  # {'total__min': *}
    context["avg"] = query.aggregate(Avg('total'))["total__avg"]  # {'total__avg': *}
    context["max"] = query.aggregate(Max('total'))["total__max"]  # {'total__max': *}

    data = [item['count'] for item in orders_count]
    payed_data = [item['count'] for item in payed_orders_count]
    labels = [item['day'].__str__() for item in orders_count]

    context["end_date"] = end_date
    context["start_date"] = start_date
    context["orders_count"] = orders.count()
    context["orders_month"] = orders_count
    context["payed_data"] = payed_data
    context["data"] = data
    context["labels"] = labels

    return render(request, "store_statistics/index.html", context=context)
