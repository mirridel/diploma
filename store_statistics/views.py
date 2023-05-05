from datetime import timedelta, datetime

from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from store.models import Order


def index(request):
    orders = Order.objects.all()

    context = dict()
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if request.POST:
        end_date = datetime.strptime(request.POST.get("end"), '%Y-%m-%d').date()
        start_date = datetime.strptime(request.POST.get("start"), '%Y-%m-%d').date()

        orders_month = Order.objects.filter(
            creation_date_time__range=(start_date, end_date)).annotate(
            day=TruncDate('creation_date_time')).values('day').annotate(count=Count('id')).order_by('day')

        if request.POST.get('spec_name') and request.POST.get('spec_val'):
            orders_month = Order.objects.filter(
                Q(creation_date_time__range=(start_date, end_date)) &
                Q(shoppingcart__product__specs__name__icontains=request.POST.get('spec_name')) &
                Q(shoppingcart__product__specs__val__icontains=request.POST.get('spec_val'))).annotate(
                day=TruncDate('creation_date_time')).values('day').annotate(count=Count('id')).order_by('day')
    else:
        orders_month = Order.objects.filter(
            creation_date_time__range=(start_date, end_date)).annotate(
            day=TruncDate('creation_date_time')).values('day').annotate(count=Count('id')).order_by('-day')

    data = [item['count'] for item in orders_month]
    labels = [item['day'].__str__() for item in orders_month]

    context["end_date"] = end_date
    context["start_date"] = start_date
    context["orders_count"] = orders.count()
    context["orders_month"] = orders_month
    context["data"] = data
    context["labels"] = labels

    return render(request, "store_statistics/index.html", context=context)
