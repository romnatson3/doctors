from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from bot.misc import DotAccessibleDict


# logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST' and request.headers.get('X-Telegram-Bot-Api-Secret-Token') == settings.X_TELEGRAM_BOT_API_SECRET_TOKEN:
        response = json.loads(request.body)
        response = DotAccessibleDict(response)
        logger.info(response)
        return HttpResponse(status=200)
    return HttpResponse(status=400)
