import re
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from chat import models as lmodels
from . import models
import re
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import forms


@api_view(["POST"])
def check_username(request):
    data = request.data
    data = data["username"]
    try:
        user = User.objects.get(username=data)
        if user is None:
            return Response('Valid username')
        else:
            return Response('Already exist')
    except:
        return Response('Valid username')

###########################################################################################################
@api_view(["POST"])
def check_email(request):
    data = request.data
    data = data["email"]
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,data)):
        try:
            User.objects.get(email=data)
            return Response('Already exist')
        except:
            return Response('Valid email')
    else:
        return Response("Invalid email")

###################################################################################################################
@api_view(['POST'])
def checkpass(request):
    data = request.data
    password = data['pass']
    if len(password) == 0:
        return Response("enter password")
    else:
        flag=0
        while True:
            if (len(password)<8):
                flag = -1
                break
            elif not re.search("[a-z]", password):
                flag = -1
                break
            elif not re.search("[A-Z]", password):
                flag = -1
                break
            elif not re.search("[0-9]", password):
                flag = -1
                break
            elif not re.search("[_@$]", password):
                flag = -1
                break
            elif re.search("\s", password):
                flag = -1
                break
            else:
                flag = 0
                break
        
        if flag ==-1:
            return Response("invalid pass")
        else:
            return Response("strong pass")

###################################################################################################################
@login_required(login_url='atent:login')
def Notfound(request):
    return render(request, 'atent/Notfound.html')

#####################################################REGISTER#########################################################

def register(request):
    try:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("chat:index"))
    except:
        pass

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user= User.objects.create_user(username, email, password)
        prof= lmodels.profile(owner_prof= user, userid= username)
        prof.save()
        user = authenticate(request, username=username, password=password)
        login(request, user)
        messages.success(request, "You successfully registered!" )
        return HttpResponseRedirect(reverse("chat:index"))

    else:
        return render(request, 'atent/register.html')

#####################################################LOGIN#########################################################

def user_login(request):
    try:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("chat:index"))
    except:
        pass
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user= User.objects.get(username=username)
            if 'next' in request.POST:
                    login(request , user)
                    user.profile.is_online = True
                    user.profile.save()
                    messages.success(request, "You successfully logged in!" )
                    return redirect(request.POST['next'])
            else:
                login(request, user)
                user.profile.is_online = True
                user.profile.save()
                messages.success(request, "You successfully logged in!" )
                return HttpResponseRedirect(reverse("chat:index"))
        else:
            messages.warning(request, "invalid login details" )
            return HttpResponseRedirect(reverse("atent:login"))
    else:
        context ={}
        context['form']= forms.LoginForm()
        return render(request, 'atent/login.html', context)

#####################################################LOGOUT######################################################

def user_logout(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            user.profile.is_online = False
            user.profile.save()
            logout(request)
            messages.success(request, "Your logged out!" )
            return HttpResponseRedirect(reverse("chat:index"))
    except:
        pass
    return HttpResponseRedirect(reverse("chat:index"))

#####################################################VERIFY_EMAIL_REQUEST#############################################

@login_required(login_url='atent:login')
def verify_email(request):
    try:
        if request.user.is_authenticated:
            print(555)
            if request.method == 'POST':
                try:
                    user = request.user
                    t = models.Token.objects.get(user_token=user, valid=0)
                    t.delete()
                except:
                    pass
                user= request.user
                token = models.Token(user_token=user , valid=0)
                token.save()
                try:
                    subject = 'Verify email'
                    message = """From: <"mysite.com">
                    Change your password
        
                    http://localhost:8000/account/verify/{num}/
                    """
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email, ]
                    
                    send_mail( subject, message.format(num = t.id), email_from, recipient_list )
                    messages.warning(request, "Please check your mailbox to VERIFY your email" )
                    return HttpResponseRedirect(reverse("chat:index"))
                except Exception:
                    messages.warning(request, "An error has occured, please try again later" )
                    return HttpResponseRedirect(reverse("chat:index"))
            user_email= request.user.email
            print(444)
            return render(request, 'atent/verify_email.html', {"email": user_email})
    except:
        return HttpResponseRedirect(reverse("atent:login"))

#####################################################VERIFY_EMAIL_CONFRIMATION#########################################

@login_required(login_url='atent:login')
def verify(request , token):
    try:
        token= models.Token.objects.get(id=token)
        user= token.user_id
        prof= lmodels.profile.objects.get(owner_prof= user)
        prof.level = 1
        prof.save()
        token.delete()
        messages.success(request, "You successfully verified your account!" )
        return HttpResponseRedirect(reverse("chat:index"))
    except:
        messages.warning(request, "Please verify your email" )
        return HttpResponseRedirect(reverse("chat:index"))

################################# CHANGE_PASSWORD_REQUEST ######################

def changepass(request):
    if request.method == "POST":
        try:
            email= request.POST['email']
            user = User.objects.get(email= email)
        except:
            messages.warning(request, "No such email! Please try another email" )
            return HttpResponseRedirect(reverse('atent:changepass'))
        
        try:
            user = User.objects.get(email= email)
            t = models.Token.objects.get(user_token=user)
            t.delete()
        except:
            pass
        t = models.Token(user_token=user, valid=1)
        t.save()
        try:
            subject = 'change password'
            message = """From: <"mysite.com">
            Subject: Change password
            Click link below to reset your password

            http://localhost:8000/account/reset-password/{num}/
            """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            
            send_mail( subject, message.format(num = t.id), email_from, recipient_list )
            messages.success(request, "Please check your email for next step." )
            return HttpResponseRedirect(reverse('atent:login'))
        except Exception as ex:
            t.delete()
            messages.warning(request, ex )
            return HttpResponseRedirect(reverse('atent:changepass'))
    return render(request, "atent/changepass.html")

############################## CHANGE_PASSWORD_CONFRIMATION ########################

def reset_password(request, token):
    if request.method == "POST":
        if request.POST["password"]== request.POST["confpassword"]:
            t = models.Token.objects.get(id=token, valid=1)
            user = User.objects.get(id=t.user_token.id)
            user.set_password(request.POST["password"])
            user.save()
            t.delete()
            messages.success(request, "Password updated successfull! Login please" )
            return HttpResponseRedirect(reverse('atent:login'))
        else:
            messages.warning(request, "Password dont match!" )
            return HttpResponseRedirect(reverse('atent:resetpassword', args=(token,)))
    else:
        try:
            t = models.Token.objects.get(id=token, valid=1)
            return render(request, "atent/reset-password.html", {"username": User.objects.get(id=t.user_token.id)})
        except Exception:
            messages.warning(request, "Sorry, your token not found." )
            return HttpResponseRedirect(reverse('atent:resetpassword', args=(token,)))


