from django.forms import ModelForm, PasswordInput
from dashboard.core.bots.models import Bot


class BotForm(ModelForm):
    class Meta:
        model = Bot
        fields = ['name', 'password', 'cpuArchitecture', 'cpuDetail', 'gpuType',
                  'gpuDetail', 'platform', 'platformDetail', 'enabled']
        widgets = {
            'password': PasswordInput(render_value = True),
        }