from django.urls import path, re_path

from . import views, cart_handler

app_name = 'store'
urlpatterns = [
    path('', views.main, name='index'),
    path('catalog/', views.CategoryListView.as_view(), name='catalog'),

    path('cart/', views.cart_view, name='cart-view'),
    path('cart_handler', cart_handler.cart_handler, name='cart-handler'),
    path('checkout/', views.checkout_view, name='checkout'),

    path('orders/', views.order_list_view, name='orders'),
    path('orders/<str:status>', views.order_list_by_status_view, name='orders-by-status'),
    path('order/<int:pk>/', views.order_detail_view, name='order-detail'),
    path('order/create/', views.OrderCreate.as_view(), name='order-create'),
    path('order/update/<int:pk>/', views.OrderUpdate.as_view(), name='order-update'),
    path('order/delete/<int:pk>/', views.OrderDelete.as_view(), name='order-delete'),

    path('category/create/', views.CategoryCreate.as_view(), name='category-create'),
    path('category/update/<int:pk>/', views.CategoryUpdate.as_view(), name='category-update'),
    path('category/delete/<int:pk>/', views.CategoryDelete.as_view(), name='category-delete'),

    re_path(r'^catalog/(?P<pk>\d+)$', views.category_detail_view, name='product-list'),
    path('product/<int:pk>/', views.product_detail_view, name='product-detail'),
    path('product/create/', views.product_create_view, name='product-create'),

    path('product/add_spec/<int:pk>/', views.add_spec_view, name='add-spec'),
    path('product/update_spec/<int:pk>/', views.SpecsUpdate.as_view(), name='update-spec'),
    path('product/delete_spec/<int:pk>/', views.SpecsDelete.as_view(), name='delete-spec'),

    path('product/create/<int:pk>/', views.product_create_view, name='product-create'),
    path('product/update/<int:pk>/', views.product_update_view, name='product-update'),
    path('product/delete/<int:pk>/', views.ProductDelete.as_view(), name='product-delete'),

    path('search/', views.search, name='search'),
    path('specs', views.specs, name='specs')
]