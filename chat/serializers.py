from rest_framework import serializers
from .models import ChatRoom, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    room_unread_messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = '__all__'

    def get_room_unread_messages(self, obj):
        user = self.context['user']
        room_unread_messages = Message.objects.filter(room=obj, is_read=False).exclude(user=user).count()
        return room_unread_messages

    def get_last_message(self, obj):
        last_message = Message.objects.filter(room=obj).last()
        if last_message:
            return last_message.message
        else:
            return None
    def get_last_message_time(self, obj):
        last_message = Message.objects.filter(room=obj).last()
        if last_message:
            return last_message.created_at
        else:
            return None