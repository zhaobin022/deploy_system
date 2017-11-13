#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from usercenter.forms import LoginForm
from usercenter.forms import EmailForm
from usercenter.models import MyUser
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.mail import send_mail
import traceback
import json


def login(request):
    user_form = LoginForm()
    email_form = EmailForm()

    if request.method == "POST":
        user_form = LoginForm(request.POST)
        if user_form.is_valid():
            remember = user_form.cleaned_data.get('remember')
            if not remember:
                request.session.set_expiry(0)
            user = auth.authenticate(**user_form.cleaned_data)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # user_form.
                user_form.add_error(NON_FIELD_ERRORS,"用户名或密码错误")
    return render(request,'user_center/login.html',locals())

@login_required
def logout(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse('login'))


@login_required
def p403(request):
    return render(request,"base/403.html")

@login_required
def p404(request):
    return render(request,"base/404.html")



def sendmail_view(request):
    user_form = LoginForm()


    if request.method == "POST":

        try:
            ret = {
                    "status" : True,
                }

            email_form = EmailForm(request.POST)

            if email_form.is_valid():

                email = email_form.cleaned_data.get("email")

                user_list = MyUser.objects.filter(email=email)
                if user_list:
                    user_obj = user_list[0]
                    user_obj.set_password('123456')
                    user_obj.save()
                    msg= u"%s 您好 你的密码已重置为 123456, 请及时修改密码!" % user_obj.username
                    send_mail('密码找回', msg, 'nonprod-monitor@tjpme.com',
                              [email], fail_silently=False)
                    ret["msg"] = '重置密码成功, 请查看邮箱并重新登录 !'

                else:
                    ret["status"] = False
                    ret["msg"] = '邮箱输入错误!'
            else:
                ret["status"] = False
                print email_form.errors.as_json(),11111
                ret["msg"] = email_form.errors.as_json()

        except Exception as e:
            traceback.print_exc()
            ret["status"] = False
            ret["msg"] = '系统内部错误 ， 请联系管理员!'

        finally:
            return render(request, 'user_center/login.html', locals())
    elif request.method == "GET":
        return HttpResponseRedirect(reverse('login'))

        #
# def sendmail_view(request):
#     if request.method == "POST":
#         try:
#             ret = {
#                 "status" : True,
#             }
#
#             email_form = EmailForm(request.POST)
#
#             if email_form.is_valid():
#
#                 email = email_form.cleaned_data.get("email")
#
#                 user_list = MyUser.objects.filter(email=email)
#                 if user_list:
#                     user_obj = user_list[0]
#                     msg= "%s 您好 你的密码已重置为 123456, 请及时修改密码!" % user_obj.username
#                     send_mail('密码找回', msg, 'nonprod-monitor@tjpme.com',
#                               [email], fail_silently=False)
#                     ret["msg"] = '重置密码成功!'
#
#                 else:
#                     ret["status"] = False
#                     ret["msg"] = '邮箱输入错误!'
#             else:
#                 ret["status"] = False
#                 ret["msg"] = email_form.as_json()
#
#         except Exception as e:
#             ret["status"] = False
#             ret["msg"] = '系统内部错误 ， 请联系管理员!'
#
#         finally:
#             return HttpResponse(json.dumps(ret))