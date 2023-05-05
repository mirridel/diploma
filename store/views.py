import os

from django import forms
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from diploma import settings
from store.models import Category, Product, Order, ShoppingCart, Specs
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import ProductCreateForm, ProductUpdateForm, AddSpecsForm, CheckoutForm, OrderForm
from .cart_handler import Cart
from .templatetags.has_group import has_group
from yoomoney import Quickpay


def main(request):
    return redirect("store:catalog")


# CATEGORY
@method_decorator(permission_required('store.category_create'), name='dispatch')
class CategoryCreate(CreateView):
    model = Category
    fields = '__all__'


@method_decorator(permission_required('store.category_update'), name='dispatch')
class CategoryUpdate(UpdateView):
    model = Category
    fields = '__all__'


@method_decorator(permission_required('store.category_delete'), name='dispatch')
class CategoryDelete(DeleteView):
    model = Category
    fields = '__all__'
    success_url = reverse_lazy('store:catalog')


class CategoryListView(generic.ListView):
    model = Category


# PRODUCTS
# CREATE
@permission_required('store.create_product')
def product_create_view(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    product = Product(category=category)

    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product_card = form.save()
            return redirect('store:product-detail', pk=product_card.id)
    else:
        return render(request, 'store/product_form.html', {'form': ProductCreateForm(instance=product)})


# UPDATE
@permission_required('store.update_product')
def product_update_view(request, pk):
    instance = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('store:product-detail', kwargs={'pk': pk}))
    return render(request, 'store/product_form.html', {'form': ProductUpdateForm(instance=instance)})


# DELETE
@method_decorator(permission_required('store.delete_product'), name='dispatch')
class ProductDelete(DeleteView):
    model = Product
    fields = '__all__'
    success_url = reverse_lazy('store:catalog')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.image.remove()
        os.remove(obj.image.path)
        return super().delete(request, *args, **kwargs)


def category_detail_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    product_list = category.product_set.all()  # получаем список всех продуктов
    min_price = request.GET.get("min_price")  # получаем минимальную цену из запроса
    max_price = request.GET.get("max_price")  # получаем максимальную цену из запроса
    if min_price:
        try:
            min_price = int(min_price)
            product_list = product_list.filter(price__gte=min_price)
        except ValueError:
            pass
    if max_price:
        try:
            max_price = int(max_price)
            product_list = product_list.filter(price__lte=max_price)
        except ValueError:
            pass
    paginator = Paginator(product_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "store/product_list.html", {"category": category, "page_obj": page_obj})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_hex = request.session.get('cart', 0)
    cart = Cart()
    cart.hex_decode(cart_hex)

    return render(
        request,
        'store/product_detail.html',
        context={'product': product, 'cart': cart.get_dict()}
    )


# SPECS
# SEARCH
def specs(request):
    search_query = request.GET.get('search_query')
    search_param = request.GET.get('search_param')

    query = Specs.objects.annotate(name_lower=Lower('name')).filter(
        name_lower__icontains=search_query).values_list('name_lower', flat=True).distinct()
    if search_param:
        query = Specs.objects.annotate(name_lower=Lower('name'), val_lower=Lower('val')).filter(
            name_lower=search_query, val_lower__icontains=search_param).values_list('val_lower', flat=True).distinct()

    response = dict()
    response['result'] = list(query.all())
    return JsonResponse(response)


# CREATE
@permission_required('store.specs_create')
def add_spec_view(request, pk=None):
    product = get_object_or_404(Product, pk=pk)
    _specs = Specs(product=product)
    if request.method == 'POST':
        form = AddSpecsForm(request.POST, instance=_specs)
        if form.is_valid():
            form.save()
            return redirect('store:product-detail', pk=product.id)
    return render(request, 'store/specs_form.html', {'form': AddSpecsForm(instance=_specs)})


# UPDATE
@method_decorator(permission_required('store.specs_update'), name='dispatch')
class SpecsUpdate(UpdateView):
    model = Specs
    fields = ["name", "description", "val"]


# DELETE
@method_decorator(permission_required('store.specs_delete'), name='dispatch')
class SpecsDelete(DeleteView):
    model = Specs
    fields = '__all__'

    def form_valid(self, form):
        pk = self.object.product.id
        self.object.delete()
        return redirect("store:product-detail", pk=pk)


# ORDERS
def order_list_view(request):
    if request.user.has_perm('store.view_order'):
        order_list = Order.objects.all()
        return render(request, 'store/order_list.html', {'order_list': order_list})
    return redirect('index')


def order_list_by_status_view(request, status):
    if request.user.has_perm('store.view_order'):
        order_list = Order.objects.filter(status__icontains=status)
        return render(request, 'store/order_list.html', {'order_list': order_list})
    return redirect('index')


def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    user = request.user

    if has_group(user, "admin") or has_group(user, "manager") or order.client == user:
        return render(request, 'store/order_detail.html', {'order': order})

    return render(request, 'access_error.html')


@method_decorator(permission_required('store.order_create'), name='dispatch')
class OrderCreate(CreateView):
    model = Order
    fields = '__all__'


@method_decorator(permission_required('store.order_update'), name='dispatch')
class OrderUpdate(UpdateView):
    model = Order
    form_class = OrderForm


@method_decorator(permission_required('store.order_delete'), name='dispatch')
class OrderDelete(DeleteView):
    model = Order
    fields = '__all__'
    success_url = reverse_lazy('store:orders')


# CART
def cart_view(request):
    _sum = 0
    cart_hex = request.session.get('cart')
    cart = Cart()
    try:
        cart.hex_decode(cart_hex)
        _sum = cart.get_total()
    except:
        request.session['cart'] = None

    return render(request, 'store/cart.html', {'cart': cart.get_products_with_price(), 'sum': _sum})


# CHECKOUT
@login_required()
def checkout_view(request):
    _sum = 0
    cart_hex = request.session.get('cart')
    cart = Cart()
    try:
        cart.hex_decode(cart_hex)
        _sum = cart.get_total()
    except:
        request.session['cart'] = None

    if request.user.is_authenticated:
        request.user.first_name = ""

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.status = "CREATED"
            order.client = request.user
            order.save()

            cart_hex = request.session.get('cart')
            cart = Cart()
            cart.hex_decode(cart_hex)

            for key, item in cart.get_dict().items():
                product = get_object_or_404(Product, pk=key)
                shopping_cart = ShoppingCart(order=order, product=product, quantity=item["quantity"],
                                             price=product.price)
                shopping_cart.save()
            request.session['cart'] = None
            # PAYMENT
            quick_pay = Quickpay(
                receiver=settings.YOOMONEY_RECEIVER,
                quickpay_form="shop",
                targets='Заказ №{}'.format(order.id),
                paymentType="SB",
                successURL=order.get_absolute_url(),
                sum=_sum,
                label='{}'.format(order.id)
            )
            return redirect(quick_pay.redirected_url)
    else:
        form = CheckoutForm()

    return render(request, 'store/checkout.html', {'sum': _sum, 'form': form})


# GLOBAL SEARCH
def search(request):
    query_str = request.GET.get("query")
    query_str = query_str.split(' ')

    results = Product.objects.all()

    for obj in query_str:
        results = results.filter(Q(title__icontains=obj) | Q(category__name__icontains=obj))

    paginator = Paginator(results, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "store/product_list.html", {"page_obj": page_obj})
