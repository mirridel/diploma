import uuid

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from account.forms import PersonalInformationForm, CaptchaRegistrationForm
from account.models import Confirmation, UserInfo
from diploma import settings


@login_required()
def account(request):
    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'account/account_view.html', context={"user_info": user_info})


@login_required()
def edit(request):
    user = User.objects.get(pk=request.user.id)
    user_info = UserInfo.objects.get(user=user)
    initial = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user_info.phone
    }

    if request.POST:
        form = PersonalInformationForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            user_info.phone = form.cleaned_data['phone']
            user_info.save()
            return redirect('account:index')
    else:
        form = PersonalInformationForm(initial=initial)
    return render(request, 'account/personal_information_form.html', context={'form': form})


@login_required()
def orders(request):
    return render(request, 'account/orders_view.html')


@login_required()
def notifications_view(request):
    return render(request, 'account/notifications_view.html')


def register_view(request):
    if request.method == "POST":
        form = CaptchaRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user_confirmation = Confirmation(user=user, _uuid=uuid.uuid4())
            userinfo = UserInfo(user=user)

            email = user.email
            data = """
                    Здравствуйте!
                    
                    Спасибо за регистрацию на нашем сайте. Для завершения регистрации и активации вашей учетной записи,
                    пожалуйста, подтвердите свой адрес электронной почты, перейдя по ссылке ниже:
                    
                    {}
                    
                    Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.
                    
                    С уважением,
                    Команда [name]
                    """

            confirmation_link = "http://{}/account/confirmation/{}/".format(request.get_host(), user_confirmation.uuid)

            context = {
                'link': confirmation_link,
                'name': settings.EMAIL_COMPANY_NAME
            }
            html_message = render_to_string('account/email/confirmation.html', context)

            send_mail(subject='Активация учетной записи',
                      message=data.format(confirmation_link),
                      from_email="mixasibb@gmail.com",
                      recipient_list=[email],
                      html_message=html_message,
                      fail_silently=False)

            user.save()
            user_confirmation.save()
            userinfo.save()

            return render(request=request, template_name="registration/register_done.html", context={"email": email})
    else:
        form = CaptchaRegistrationForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


def email_confirmation(request, token):
    try:
        user_confirmation = get_object_or_404(Confirmation, _uuid=token)
        user = user_confirmation.user
        user.is_active = True
        user.save()
        login(request, user)
        user_confirmation.delete()
        return redirect('index')
    except Exception as ex:
        print(ex)
        return HttpResponse(ex)


def register_done(request):
    return render(request=request, template_name="registration/register_done.html")
