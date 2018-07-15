from rest_framework import authentication, exceptions
from dashboard.core.bots.models import Bot


class BotAuthentication(authentication.BaseAuthentication):
    """
    Bot authentication view, used to authenticate data sending bots via API
    """

    def authenticate(self, request):
        bot_name = request.POST.get('bot_id')
        bot_password = request.POST.get('bot_password')

        if not bot_name or not bot_password:
            return None

        try:
            bot = Bot.objects.get(name=bot_name)
            if bot.password != bot_password:
                raise exceptions.AuthenticationFailed('Bad authentication details')
        except Bot.DoesNotExist:
            raise exceptions.AuthenticationFailed('This bot cannot be authenticated')

        return (bot, bot_name)
