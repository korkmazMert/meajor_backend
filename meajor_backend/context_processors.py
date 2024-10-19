from accounts.models import ActivationUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta  


class UserActivation:
    def __init__(self, request):
        """
        UserActivation objesi oluşturulurken.
        """
        self.session = request.session
        activation = self.session.get(settings.USER_SESSION_ID)
        self.activation = activation.copy() if activation else {}
        try:
            last_user = ActivationUser.objects.last().user_secret
            last_user = int(last_user) + 1
        except:
            last_user = 1
        if self.activation == {}:
            my_user = ActivationUser.objects.create(user_secret = last_user)
            self.activation[str(my_user.user_secret)] = 'active'
        else:
            my_id = ''
            for item in self.activation.keys():
                my_id = str(item)
            exist_active = ActivationUser.objects.filter(user_secret = my_id).first()
            exist_active.last_activity = timezone.now()
            exist_active.save()
        self.save()

    def save(self):
        self.session[settings.USER_SESSION_ID] = self.activation
        self.session.modified = True
    
    def get_my_user(self):
        my_user = self.activation.keys()
        return my_user

    def get_total_users(self):
        """
        Aktif kullanıcı adedini verir
        """
        online_users = ActivationUser.objects.filter(last_activity__gte = timezone.now() - timedelta(minutes=5)).count()
        return online_users




def user_activation(request):
    return {'activation':UserActivation(request)}


def get_info(request):
    try:
        # get control_id
        my_activation_user = 'null'

        if request.user.is_authenticated:
            my_activation_user = request.user.id
        else:
            active_users = UserActivation(request)
            my_activation_user = list(active_users.get_my_user())[0]
        
        return {'my_activation_user': my_activation_user}
    except:
        return {'my_activation_user': 'null'}
    
