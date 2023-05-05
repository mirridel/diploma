from django.contrib import admin

# Register your models here.
from store.models import Category, ShoppingCart, Order, Product, Specs


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'price', 'description']
    list_display = ['id', 'category', 'title', 'price', 'quantity']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'total', 'status']


class CartAdmin(admin.ModelAdmin):
    search_fields = ['order__id']
    list_display = ['id', 'order', 'product', 'quantity', 'price']


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Specs)
admin.site.register(ShoppingCart, CartAdmin)
admin.site.register(Order, OrderAdmin)
