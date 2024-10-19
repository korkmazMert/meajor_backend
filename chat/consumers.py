import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom,Message
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):



    @database_sync_to_async
    def check_receiver_online(self, user_id):
       try:
            room = ChatRoom.objects.filter(id=self.room_name).first()
            print('room.online_users: ',room.online_users)
            online_users_temp = list(json.loads(room.online_users)) if room.online_users else []
            len_before = len(online_users_temp)
            online_users_temp.remove(str(user_id))
            len_after = len(online_users_temp)
            if len_after >  0 :
                is_read = True
            else:
                is_read = False
            return is_read
       except Exception as e:
              print('error:',e)
              return False
    

    @database_sync_to_async
    def save_message_to_db(self, msg, user_id,user_active,sender_name,is_read=False):
        
        read_time = None
        if is_read:
            read_time = datetime.now()        
        if user_active:
            return Message.objects.create(
                room_id=self.room_name, 
                message=msg, 
                user_id=user_id, 
                is_read=is_read,
                read_time=read_time, 
                is_auth_user=True
                )
        else:
            return Message.objects.create(
                room_id=self.room_name, 
                message=msg, 
                anonymous_user_secret=user_id,
                is_read=is_read, 
                read_time = read_time, 
                is_auth_user=False, 
                sender_name=sender_name
                )
    
    @database_sync_to_async
    def set_online_user(self, room_id, current_user):
        room = ChatRoom.objects.get(id=room_id)
        # Decode online_users from JSON, ensuring it's a list if empty or None
        online_users = json.loads(room.online_users) if room.online_users else []
        if current_user not in online_users:
            online_users.append(current_user)
        # Encode online_users back to JSON before saving
        room.online_users = json.dumps(online_users)
        room.save()

    @database_sync_to_async
    def delete_online_user(self, room_id, current_user):
        room = ChatRoom.objects.get(id=room_id)
        # Decode online_users from JSON, ensuring it's a list if empty or None
        online_users = json.loads(room.online_users) if room.online_users else []
        if current_user in online_users:
            print("online users before: ", online_users)
            online_users.remove(current_user)
            print("online users after: ", online_users)
        # Encode online_users back to JSON before saving
        room.online_users = json.dumps(online_users)
        room.save()


    @database_sync_to_async
    def get_user_name_or_secret(self, message):
        return f'{message.user.first_name} {message.user.last_name}' if message.user else message.sender_name
    
    @database_sync_to_async
    def get_user_id(self, message):
        return message.user_id if message.user_id else message.anonymous_user_secret
    
    @database_sync_to_async
    def get_read_time(self, message):
        return message.read_time.strftime("%Y-%m-%d %H:%M:%S") if message.read_time else None
    
    
    
    @database_sync_to_async
    def get_messages(self, pageNumber=1, offset=0, limit=10):
        offset = pageNumber - 1
        messages = Message.objects.filter(room_id=self.room_name).order_by('-created_at')[offset*limit:(offset+1)*limit]
        print('messages',messages)
        return messages[::-1]
    
    @database_sync_to_async
    def set_message_as_read(self): 
        messages = Message.objects.filter(room_id=self.room_name, is_read = False)
        print('set_message_as_read',messages)
        
        for message in messages:
            sender_id = message.user_id if message.user_id else message.anonymous_user_secret
            print('message sender_id', sender_id, 'type:', type(sender_id))
            print('message control_id', self.control_id, 'type:', type(self.control_id))
            if int(sender_id) != int(self.control_id):
                print('message is read',message.is_read)
                message.is_read = True
                if not message.read_time:
                    message.read_time = datetime.now()
                message.save()
    
    @database_sync_to_async
    def get_message_detail(self, message_id):
        message = Message.objects.get(id=message_id)
        return message
    
    async def fetch_more_messages(self, pageNumber):
        print("FETCHING MORE MESSAGES")
        more_messages = await self.get_messages(pageNumber = pageNumber)
        more_messages = more_messages[::-1]
        print('more_messages',more_messages)
        for message in more_messages:
            user_name_or_secret = await self.get_user_name_or_secret(message)
            user_id = await self.get_user_id(message)
            await self.send(text_data=json.dumps({
                "type": "fetch_more_messages",
                "message": message.message,
                "user_id": user_id,
                "is_read": message.is_read,
                "user_name": user_name_or_secret,
                "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }))
        
    
    async def connect(self):
        print("CONNECTED")
        self.control_id = self.scope["url_route"]["kwargs"]["control_id"]

        # Add the user to a group based on their control_id
        self.user_group_name = f"user_{self.control_id}"
        print('user_group_name:',self.user_group_name)
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()

    async def init_messaging(self,room_id):
        self.room_name = room_id
        print('init_messagingggg room_name:',self.room_name)
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.join',
            }
        )
        await self.init_chat()

      
        
    async def dispose_messaging(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.leave',
            }
        )
        print("CHAT LEAVE control id:",self.control_id)
        await self.delete_online_user(room_id = self.room_name,current_user= self.control_id)
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
            )
      
        

    async def disconnect(self, close_code):
        print("DISCONNECTED")
        
        
        # close user connection to self group
        await self.channel_layer.group_discard(
            self.user_group_name, 
            self.channel_name
            )
            
       

    async def room_created(self, event):
        """
        This method is called when the `room_created` event is received.
        """
        # Send a message down to the client

        print('room_created event:',event)  
        await self.send(text_data=json.dumps({
            'type': 'room_created',
            'room': event['room'],
            }))
     

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(self.scope['session'])
        print('text_data',text_data)
   
        print("RECEIVED")
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'get_message':
            await self.get_message(text_data_json)
            return
        if message_type == 'init_messaging':
            await self.init_messaging(text_data_json.get('room_id'))
            return
        if message_type == 'dispose_messaging':
            await self.dispose_messaging()
            return
        if message_type == 'init_chat':
            await self.init_chat()
            return
        if message_type == 'fetch_more_messages':
            offset = text_data_json.get('offset')
            await self.fetch_more_messages(offset)
            return
        

        message = text_data_json["message"]
        user_name = text_data_json["user_name"]
        user_id = text_data_json["user_id"]
        date = text_data_json["date"]
        time = text_data_json["time"]
        user_active = text_data_json["user_active"]
        receiver_id = text_data_json["receiver_id"]
        print('self', self)
        print('text_data_json',text_data_json)


        isRead = await self.check_receiver_online(user_id)
        print('isRead',isRead)
        new_msg = await self.save_message_to_db(message, user_id,user_active,user_name,is_read=isRead)
        print('new_msg',new_msg)
        
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "chat.message",  
                "message_id": new_msg.id,
                "message": message,
                "user_id": user_id,
                "user_name": user_name,
                "date": date,
                "time": time,
                "is_read": isRead,
                "receiver_id": receiver_id

              
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print("CHATMMESSAGE")
        print('event',event)
        message = event["message"]
        message_id = event["message_id"]
        user_name = event["user_name"]
        date = event["date"]
        time = event["time"]
        user_id = event["user_id"]
        is_read = event["is_read"]
        receiver_id =  event["receiver_id"]
        event["room_id"] = self.room_name
    
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "new_message",
            "message": message, 
            "message_id": message_id,
            "user_id": user_id, 
            "user_name": user_name , 
            "date": date, 
            "time": time,
            "is_read": is_read,
            "receiver_id": receiver_id
            }))
        await self.notify_receiver(event)
    ## Getting message title before changing content of it
    async def get_message(self, event):
        print("EDIT MESSAGE")
        print('event',event)
        message_id = event["message_id"]

        message_detail = await self.get_message_detail(message_id)
        
    
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "get_message",
            "message_id": message_id,
            "message_title": message_detail.message
            }))
    
    # async def change_message(self, event):
    #     print("EDIT MESSAGE")
    #     print('event',event)
    #     message_id = event["message_id"]

    #     message_detail = await self.get_message_detail(message_id)
        
    
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         "type": "edit_message",
    #         "message_id": message_id,
    #         "message_title": message_detail.message
    #         }))


        
    async def notify_receiver(self, event):
        print("NOTIFY RECEIVER")
        print('event',event)
        room_id = event["room_id"]  
        message = event["message"]
        message_id = event["message_id"]
        user_name = event["user_name"]
        date = event["date"]
        time = event["time"]
        user_id = event["user_id"]
        is_read = event["is_read"]
        receiver_id =  event["receiver_id"]
        print('receiiiiver_idddddd',receiver_id)
    
        # Send message to WebSocket
        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                "type": "notify_new_message",
                "room_id": room_id,
                "message_id": message_id,
                "message": message,
                "user_id": user_id,
                "user_name": user_name,
                "date": date,
                "time": time,
                "is_read": is_read,
                "receiver_id": receiver_id
            }
        )

    async def notify_new_message(self, event):
        print("NOTIFY NEW MESSAGE")
        print('event',event)
        room_id = event["room_id"]  
        message = event["message"]
        message_id = event["message_id"]
        user_name = event["user_name"]
        date = event["date"]
        time = event["time"]
        user_id = event["user_id"]
        is_read = event["is_read"]
        receiver_id =  event["receiver_id"]
    
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "notify_new_message",
            "room_id": room_id,
            "message": message, 
            "message_id": message_id,
            "user_id": user_id, 
            "user_name": user_name , 
            "date": date, 
            "time": time,
            "is_read": is_read,
            "receiver_id": receiver_id
            }))
        

    async def init_chat(self):
        # Fetch messages from the database
        messages = await self.get_messages()
        print('messages length: ',messages.__len__())

        # Send messages to the client
        for message in messages:
            user_name_or_secret = await self.get_user_name_or_secret(message) 
            sender_id = await self.get_user_id(message)
            read_time = await self.get_read_time(message)
            print('reaaad_time',read_time)

            await self.send(text_data=json.dumps({
                "type": "init_chat",
                "message_id" : message.id,
                "message": message.message, 
                "user_id": sender_id,
                "user_name": user_name_or_secret,
                "is_read": message.is_read,
                "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "read_time" :read_time
            }))

    # Handler for when a user joins
    async def chat_join(self, event):
        print("CHAT JOIN control id:",self.control_id)
        print("CHAT JOIN room name:",self.room_name)

        await self.set_online_user(room_id = self.room_name,current_user= self.control_id)
        await self.set_message_as_read()
        is_read = await self.check_receiver_online(self.control_id)
        if is_read:
        # Send a message to WebSocket
            await self.send(text_data=json.dumps({
                'message': "someone has entered the chat room.",
                'type': 'connected',
                'user_id': int(self.control_id),
                'receiver_online': is_read
            }))
        else:
            await self.send(text_data=json.dumps({
                'message': "someone has entered the chat room.",
                'type': 'connected',
                'user_id':  int(self.control_id)
            }))

    # Handler for when a user leaves
    async def chat_leave(self, event):
        # Send a message to WebSocket
        await self.send(text_data=json.dumps({
            'message': "someone has leaved the chat room.",
            'type': 'disconnected',
            'user_id': int(self.control_id)
        }))


