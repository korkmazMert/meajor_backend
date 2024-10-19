from django.shortcuts import render
from django.http import JsonResponse
from meajor_backend.context_processors import UserActivation
from .models import ChatRoom, Message
from accounts.models import User
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import ChatRoomSerializer
import json

# Create your views here.
def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})



def open_live_support(request):
    participant = {}
    user_name = 'Misafir Kullanıcı'
    user_active = False
    my_activation_user = 'null'

    if request.user.is_authenticated:
        print ("open_live_support user id: ",request.user.id)
        user_name = f'{request.user.first_name} {request.user.last_name}'
        user_active = True
        my_activation_user = request.user.id
        participant['sender_name'] = user_name
        print('participant sender_name:',participant['sender_name'])
    else:
        active_users = UserActivation(request)
        my_activation_user = list(active_users.get_my_user())[0]

        get_user_info  = active_users.get_user_info()  # No need to convert to list
        print("get_user_info:",get_user_info)
        guest_email = get_user_info['email']
        guest_phone = get_user_info['phone']
        guest_name = get_user_info['name']
        
        print("GET RROMM:my_activation_user", my_activation_user)

    
    participant['sender_id'] = int(my_activation_user)
    

    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        if receiver_id is not None:
            print("receiveeer_id:",receiver_id)
            participant['receiver_id'] = int(receiver_id)
        if receiver_id is None:
            receiver_id = 1
            participant['receiver_id'] = 1
        
        if request.user.is_authenticated:
            
            try:
                print("getting ")
                room = ChatRoom.objects.filter(
                    Q(participant__icontains=int(my_activation_user)) & Q(participant__icontains=int(receiver_id))
                ).first()
                print("rrrrrroom:", room)
                print(room.participant)
                participant = room.participant[0]
            except Exception as e:
                print("authenticated exception:",e)
                
                
                if receiver_id is not None:
                    participant['receiver_id'] = int(receiver_id)
                    receiver_user = User.objects.get(id=receiver_id)
                    sender_user = User.objects.get(id=my_activation_user)
                    receiver_name =  f'{receiver_user.first_name} {receiver_user.last_name}'
                    sender_name = f'{sender_user.first_name} {sender_user.last_name}'
                    participant['receiver_name'] = receiver_name
                    participant['sender_name'] = sender_name
                    participant['guest_email'] = sender_user.email
                    participant['guest_phone'] = sender_user.phone
                    room = ChatRoom.objects.create(title=participant['sender_name'], 
                                                   control_id=my_activation_user, 
                                                   is_customer=True, 
                                                   participant=[participant])
                    print("receiveeerid:",receiver_id)
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{receiver_id}",
                        {
                            'type': 'room_created',
                            'room': {
                                'id': room.id,
                                'title': room.title,
                                'is_cargo': room.is_cargo,   
                                'is_customer': room.is_customer,
                                'is_guest': room.is_guest,
   
                            }
                        }
                    )
                else:
                    participant['receiver_id'] = 1
                    room = ChatRoom.objects.create(title=participant['sender_name'], control_id=my_activation_user, participant=[participant],is_customer=True)
        else:
            try:
                room = ChatRoom.objects.filter(
                    Q(participant__icontains=int(my_activation_user)) & Q(participant__icontains=int(receiver_id))
                ).first()
                print('room.participant',room.participant)
                participant = room.participant[0]
            except:
                
                
                participant['sender_name'] = guest_name
                
                participant['guest_phone'] = guest_phone
            
                participant['guest_email'] = guest_email
                
                if receiver_id is not None:
                    participant['receiver_id'] = int(receiver_id)
                    room = ChatRoom.objects.create(title= participant['sender_name'] , 
                                                control_id=my_activation_user, 
                                                is_guest=True, 
                                                participant=[participant],
                                                )
                    print("receiveeerid:",receiver_id)
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{receiver_id}",  # The receiver's group name is 'user_{user_id}'
                        {
                            'type': 'room_created',
                            'room': {
                                'id': room.id,
                                'title': room.title,
                                'is_cargo': room.is_cargo,   
                                'is_customer': room.is_customer,
                                'is_guest': room.is_guest,
                            }
                        }
                    )
                else:
                    participant['receiver_id'] = 1
                    room = ChatRoom.objects.create(title= participant['sender_name'] , 
                                                control_id=my_activation_user, 
                                                is_guest=True, 
                                                participant=[participant],
                                                )
        # how many messages will be shown in the page, make this same with consumer.get_messages functions limit
        limit = 5
        messages_page_length = (Message.objects.filter(room_id=room.id).order_by('created_at').__len__())/limit
        print("messages_page_length:",messages_page_length)    
        fake_context = {'user': request.user}
        room_serialized = ChatRoomSerializer(room, context=fake_context).data
        context = {
            'my_activation_user':my_activation_user,
            'user_active':user_active,
            'control_id':my_activation_user,
            'room':room_serialized,
            'room_id':room.id,
            'user_name':user_name,
            'participant':participant,
            'messages_page_length':messages_page_length
        }
        print("contextxx:",context) 
        print("participant:",participant)
        print("created room_id:",room.id)
        return JsonResponse(context, status=200)
    else:
        room_id = 'null'

    # get messages
    messages_page_length = Message.objects.filter(room_id=room_id).order_by('created_at')
    print("messages_page_length:",messages_page_length)
    

    context = {
        'my_activation_user':my_activation_user,
        'user_active':user_active,
        'control_id':my_activation_user,
        'room_id':room_id,
        'user_name':user_name,
        'messages_page_length':messages_page_length
    }

    return JsonResponse(context, status=200)


def get_chatroom(request):
    try:
        room_id = request.POST.get('room_id')
        room = ChatRoom.objects.filter(id=room_id).first()
        print('room : ',room)
        fake_context = {'user': request.user}
        serialized_room = ChatRoomSerializer(room, context=fake_context).data
   
        return JsonResponse(serialized_room, safe=False)
    except Exception as e:
        context = {
            'result': 'failed',
            'message': str(e)
        }
        return JsonResponse(context, safe=False)
def get_chatrooms(request):
    if request.user.is_authenticated:
            my_activation_user = request.user.id
            user_active = True
    else:
        active_users = UserActivation(request)
        my_activation_user = int(list(active_users.get_my_user())[0])
        user_active = False
    
    all_rooms = ChatRoom.objects.filter(
        Q(participant__contains=[{'receiver_id': request.user.id}]) | 
        Q(participant__contains=[{'sender_id': request.user.id}])
    ).distinct().order_by('-updated_at')
    print("chat_rooms:",all_rooms)
    


    
    for room in all_rooms:

        room_unread_messages = Message.objects.filter(room = room, is_read = False).exclude(user = request.user).count()

        if not room_unread_messages == 0:
            room.unread_count = room_unread_messages


        try:
            room.last_message = Message.objects.filter(room = room).last().message
            room.last_message_time = Message.objects.filter(room = room).last().created_at
        except:
            room.last_message = ''  


        if room.is_cargo:
            unread_messages = Message.objects.filter(room = room, is_read = False).exclude(user = request.user)
            print("received_messages:",unread_messages)
            room.state = "cargo"
        elif room.is_customer:
            room.state = "customer"
        elif room.is_guest:
            room.state = "guest"
        elif room.is_seller:
            room.state = "seller"
    fake_context = {'user': request.user}
    serialized_chatrooms = ChatRoomSerializer(all_rooms, many=True, context=fake_context).data
    if request.user.is_authenticated:
        my_activation_user = request.user.id
        user_active = True
    else:
        active_users = UserActivation(request)
        my_activation_user = int(list(active_users.get_my_user())[0])
        user_active = False
    context = {
    'result': 'success',
    'message': 'chat rooms fetched successfuly',
    'all_chat_rooms': serialized_chatrooms,
    'my_activation_user': my_activation_user,
    'user_active': user_active
    } 
    return JsonResponse(context, safe=False)


def check_receiver_online(request):
    if request.method == 'POST':
        try:
            room_id = request.POST.get('room_id')
            room = ChatRoom.objects.filter(id=room_id).first()
            print('room.online_users: ',room.online_users)
            online_users_temp = list(json.loads(room.online_users)) if room.online_users else []
            len_before = len(online_users_temp)
            try:
                # get control_id
                my_activation_user = 'null'

                if request.user.is_authenticated:
                    print ("open_live_support user id: ",request.user.id)
                    user_name = f'{request.user.first_name} {request.user.last_name}'
                    user_active = True
                    my_activation_user = request.user.id
                else:
                    active_users = UserActivation(request)
                    my_activation_user = list(active_users.get_my_user())[0]
                    print("GET RROMM:my_activation_user", my_activation_user)
                
            except:
                pass    
            try:
                online_users_temp.remove(str(my_activation_user))
            except:
                pass
            len_after = len(online_users_temp)
            if len_after >  0 :
                is_read = True
            else:
                is_read = False
            print('check_receiver_online',is_read)
            
            return JsonResponse({'status':'success', 'online_users':len_after, 'is_receiver_online':is_read})
        except:
            return JsonResponse({'status':'failed'})
 
