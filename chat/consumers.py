import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import sync_to_async
from . import models
from django.contrib.auth.models import User
from django.db.models import Q


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        rom= models.Roomcode.objects.filter(code= self.room_name)
        romsender= rom[0].sender
        romsender2= rom[1].sender
        romreceiver= rom[0].receiver
        romreceiver2= rom[1].receiver
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        if romsender.username == self.user.username:
            if romreceiver.username == romsender2.username:
                romtst= rom[1]
                romtst.receiveronchat = True
                romtst.save()
        elif romsender2.username == self.user.username:
            if romreceiver.username == romsender2.username:
                romtst= rom[0]
                romtst.receiveronchat = True
                romtst.save()


    def disconnect(self, close_code):
        rom= models.Roomcode.objects.filter(code= self.room_name)
        romsender= rom[0].sender
        romreceiver= rom[0].receiver
        romsender2= rom[1].sender
        romreceiver2= rom[1].receiver

        if romsender.username == self.user.username:
            if romreceiver.username == romsender2.username:
                romtst= rom[1]
                romtst.receiveronchat = False
                romtst.save()
        elif romsender2.username == self.user.username:
            if romreceiver2.username == romsender.username:
                romtst4= rom[0]
                romtst4.receiveronchat = False
                romtst4.save()

        # Leave room group
        self.user = self.scope["user"]
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            username = text_data_json['username']
            receivername = text_data_json['receivername']
            message = text_data_json['message']
            self.save_message(username, receivername, message)
            msg= models.Message.objects.get(sender__username=username, receiver__id= receivername, content=message)
            msg= msg.id

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'receivername': receivername,
                    'msgid': msg
                }
            )
        except:
            message = text_data_json['msg']
            msg= models.Message.objects.get(id= message)
            msgid= msg.id
            msg.delete()
            
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msgid': msgid,
                }
            )

    # Receive message from room group
    def chat_message(self, event):
        # For Create Message
        try:
            message = event['message']
            username = event['username']
            msgid = event['msgid']

            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'message': message,
                'username':username,
                'messageid': msgid

            }))

        # For Delete Message
        except:
            messageid= event['msgid']
            self.send(text_data=json.dumps({
                'msgid': messageid,
            }))

    def save_message(self, username, receivername, message):
        receiver= User.objects.get(id = int(receivername))
        sender= User.objects.get(username = username)
        models.Message.objects.create(sender=sender, receiver=receiver, content=message)


        
