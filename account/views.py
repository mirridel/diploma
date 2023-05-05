import uuid

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from account.models import Confirmation, UserInfo
from diploma import settings
from diploma.forms import NewUserForm


@login_required()
def account(request):
    return render(request, 'account/account_view.html')


@login_required()
def edit(request):
    return render(request, 'account/orders_view.html')


@login_required()
def orders(request):
    return render(request, 'account/orders_view.html')


@login_required()
def notifications_view(request):
    email = "mixasibb@gmail.com"
    data = """
        Hello there!

        I wanted to personally write an email in order to welcome you to our platform.
         We have worked day and night to ensure that you get the best service. I hope
        that you will continue to use our service. We send out a newsletter once a
        week. Make sure that you read it. It is usually very informative.

        Cheers!
        ~ Name
            """
    send_mail('Welcome!', data, "Name",
              [email], fail_silently=False)

    return render(request, 'account/notifications_view.html')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
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

            confirmation_link = "http://{}/account/confirmation/{}/".format("37.194.20.87:8000", user_confirmation._uuid)

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
        form = NewUserForm()
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
        pass

    return HttpResponse(token)


def register_done(request):
    return render(request=request, template_name="registration/register_done.html")
