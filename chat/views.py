from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from itertools import chain
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from . import models
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["POST"])
def checkseen(request, pk):
    check= models.Roomcode.objects.filter(code= pk)
    if check[0].sender == request.user:
        if check[0].receiveronchat == True:
            return Response('receiver is on chat')
        return Response("receiver not in chat")
        
    elif check[1].sender == request.user:
        if check[1].receiveronchat == True:
            return Response('receiver is on chat')
        return Response("receiver not in chat")

    else:
        return Response("receiver not in chat")

############################## Home page ##################################
@login_required(login_url='atent:login')
def Index(request):
    try:
        Search= request.GET["search"]
        users= models.profile.objects.filter(Q(userid__icontains= Search) | Q(owner_prof__username__icontains= Search))
    except:
        users= models.profile.objects.all()
    return render(request, 'chat/index.html', {"users":users})

############################# users profile ##############################
@login_required(login_url='atent:login')
def profile(request, pk):
    ######## Checking existance of profile ########
    try:
        user= User.objects.get(id=pk)
    except:
        messages.error(request, 'No such user')
        return HttpResponseRedirect(reverse("atent:Notfound"))
    try:
        prof= models.profile.objects.get(owner_prof= user)
    except:
        messages.error(request, 'No such profile')
        return HttpResponseRedirect(reverse("atent:Notfound"))
    if prof.owner_prof.id == request.user.id:
        try:
            roomcode= models.Roomcode.objects.filter(sender=request.user, receiver=request.user)
        except:
            pass
        if len(roomcode)==0:
            code= models.Roomcode(sender=request.user, receiver=request.user)
            code.save()
            roomcode= code.code
        else:
            roomcode= roomcode[0].code

        chats= models.Roomcode.objects.filter(receiver= user)
        stahc= models.Roomcode.objects.filter(sender=user)

        ######## Sorting messsages of chatroom ########
        chat1 = [i for i in chats]
        chat2 = [i for i in stahc]
        allchat = chat1 + chat2
        unique_list = []
        for x in allchat:
            if x not in unique_list:
                unique_list.append(x)
        context= {"prof": prof, "allchats":unique_list, "roomcode":roomcode}
        return render(request, 'chat/profile.html', context)
    else:
        try:
            roomcode= models.Roomcode.objects.filter(sender=request.user, receiver=user) or models.Roomcode.objects.filter(sender=user, receiver=request.user)
        except:
            pass
        if len(roomcode)==0:
            code= models.Roomcode(sender=request.user, receiver=user)
            code.save()
            code2= models.Roomcode(sender=user, receiver=request.user)
            code2.code = code.code
            code2.save()
            roomcode= code.code
        else:
            roomcode=roomcode[0].code

        context= {"prof": prof, "roomcode":roomcode}
        return render(request, 'chat/profile.html', context)

################# User Private Chatroom #############
@login_required(login_url='atent:login')
def privatems(request, pk):
    romcode = models.Roomcode.objects.filter(code=pk)
    if romcode[0].sender.id == request.user.id or romcode[0].receiver.id == request.user.id:
        pass
    else:
        messages.error(request, "You are not aloowed!")
        return HttpResponseRedirect(reverse("chat:profile", args=(request.user.id,)))
    try:
        if request.user.id == romcode[0].sender.id:
            receiver= romcode[0].receiver
        else:
            receiver= romcode[0].sender
    except:
        messages.error(request, "No such conversion!")
        return HttpResponseRedirect(reverse("atent:Notfound"))
    sender= request.user
    useronline= models.profile.objects.filter(owner_prof= receiver).get()
    online= useronline.is_online

    ### Preperation of chatroom ###
    chats= models.Message.objects.filter(receiver= receiver, sender=sender)
    chats2= models.Message.objects.filter(receiver= sender, sender=receiver)

    ### sorting mesage by id ###
    result_list = sorted(
    chain(chats, chats2),
    key=lambda instance: instance.id)
    context = {"allchats":result_list, "online":online, "receiver":receiver, "pk":pk, "roomcode":romcode[0].code }
    return render(request, 'chat/chatroom.html', context)

#################### user edit profile ##########
@login_required(login_url='atent:login')
def editprof(request, pk):

    ######## Checking existance of profile that will be edit ########
    try:
        prof= models.profile.objects.get(id=pk)
    except:
        messages.error(request, "No such profile!")
        return HttpResponseRedirect(reverse("atent:Notfound"))
    
    ######## Checking profile ########
    if request.user == prof.owner_prof:
        if request.method=='POST':
            prof= models.profile.objects.get(id=pk)
            user= User.objects.get(profile= prof)

            ######## Checking username ########
            try:
                prof_username = request.POST['username']
                if len(prof_username) == 0:
                    pass
                else:
                    try:
                        userr= User.objects.filter(username= prof_username)
                        if len(userr) == 0:
                            user.username= prof_username
                            user.save()
                        else:
                            messages.warning(request, "Username already taken!")
                            return HttpResponseRedirect(reverse("chat:editprof", args=(prof.id,)))
                    except:
                        pass
            except:
                pass
            ######## Checking email ########
            try:
                prof_email = request.POST['email']
                if len(prof_email) == 0:
                    pass
                else:
                    try:
                        email= User.objects.filter(email= prof_email)
                        if len(email) == 0:
                            user.email= prof_email
                            user.save()
                        else:
                            messages.warning(request, "Email already taken!")
                            return HttpResponseRedirect(reverse("chat:editprof", args=(prof.id,)))
                    except:
                        pass
            except:
                pass

            ######## Checking phone number ########
            try:
                value= request.POST['phone']
                if len(value) == 0:
                    pass
                else:
                    lst= [i for i in value]
                    del lst[0]
                    phone= "".join(lst)
                    if phone.isdigit():
                        if len(phone) <= 13:
                            prof.phone_number = value
                            prof.save()
                        else:
                            messages.warning(request, "Wrong phone number format!")
                            return HttpResponseRedirect(reverse("chat:editprof", args=(prof.id,)))
                    else:
                        messages.warning(request, "Wrong phone number format!")
                        return HttpResponseRedirect(reverse("chat:editprof", args=(prof.id,)))
            except:
                pass

            
            ######## Checking userid ########
            try:
                prof_userid= request.POST['userid']
                if len(prof_userid) == 0:
                    pass
                else:
                    try:
                        proff= models.profile.objects.filter(userid= prof_userid)
                        if len(proff) == 0:
                            prof.userid= prof_userid
                            prof.save()
                        else:
                            messages.warning(request, "Userid already taken!")
                            return HttpResponseRedirect(reverse("chat:editprof", args=(prof.id,)))
                    except:
                        pass
            except:
                pass

            ######## about ########
            try:
                prof.about= request.POST['about']
                prof.save()
            except:
                pass

            ######## picture ########
            try:
                upload = request.FILES['upload']
                fss = FileSystemStorage()
                file = fss.save(upload.name, upload)
                prof.picture= upload
                prof.save()
            except:
                pass

            prof= models.profile.objects.get(id=pk)
            userr= User.objects.get(profile= prof)
            messages.success(request, "You profile has been edited")
            return HttpResponseRedirect(reverse("chat:profile", args=(userr.id,)))

        prof= models.profile.objects.get(id=pk)    
        return render(request, 'chat/editprof.html', {"prof":prof})
    else:
        messages.error(request, "Not allowed!")
        return HttpResponseRedirect(reverse("atent:Notfound"))