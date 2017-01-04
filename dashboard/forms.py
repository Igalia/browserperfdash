from django.forms import ModelForm, PasswordInput
from .models import Bot


class BotForm(ModelForm):
    class Meta:
        model = Bot
        fields = ['name', 'password', 'cpuArchitecture', 'cpuDetail', 'gpuType',
                  'gpuDetail', 'platform', 'platformDetail', 'enabled']
        widgets = {
            'password': PasswordInput(),
        }