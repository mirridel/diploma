from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.contrib.staticfiles.urls import static

from account.views import register_request
from diploma import views, settings

# TODO: + ПРИВЯЗКА ПОЧТЫ
# + СМЕНА ПАРОЛЯ
# + ПРИ ОПЛАТЕ МЕНЯЛСЯ QUANTITY ПРОДУКТА
# ? СТРАНИЦА С ОШИБКОЙ


urlpatterns = [
    path('', views.main, name='index'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('store/', include('store.urls')),
    path('statistics/', include('store_statistics.urls')),

    path('success/', views.success, name="success"),
    path('update', views.ajax_update, name='update'),
]

urlpatterns += [
    path('404', views.page_not_found_view, name='404')
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', views.login_view, name='clogin'),
    path('accounts/register/', register_request, name='register')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "diploma.views.page_not_found_view"
