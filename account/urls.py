from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.account, name='index'),
    path('edit/', views.edit, name='edit'),
    path('orders/', views.orders, name='orders'),
    path('notifications/', views.notifications_view, name='notifications'),

    path('confirmation/<uuid:token>/', views.email_confirmation, name='email-confirmation'),

    path('register/done/', views.register_done, name='email-confirmation')
]