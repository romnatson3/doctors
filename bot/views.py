from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from bot.misc import DotAccessibleDict
from bot.tasks import send_message_to_new_user, send_message_specialities, \
    send_message_districts, send_message_doctor
from bot.models import User, Doctor
from bot.misc import send_message
from bot import texts


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST' and request.headers.get('X-Telegram-Bot-Api-Secret-Token') == settings.X_TELEGRAM_BOT_API_SECRET_TOKEN:
        body = json.loads(request.body)
        body = DotAccessibleDict(body)
        logging.debug(body)
        # return HttpResponse(status=200)
        if body.message.text:
            message = body.message
            logging.info(f'Incoming message from: {message.from_user.id} {message.from_user.username}, {message.text}')
            if message.text == '/start':
                if not User.objects.filter(id=message.from_user.id).exists():
                    user = User.objects.create(
                        id=message.from_user.id,
                        username=message.from_user.username if message.from_user.username else None,
                        first_name=message.from_user.first_name if message.from_user.first_name else None,
                        last_name=message.from_user.last_name if message.from_user.last_name else None,
                    )
                    logging.info(f'Create new user: {user.id} {user.username} {user.first_name} {user.last_name}')
                send_message_to_new_user.delay(message.from_user.id)
            elif message.text == 'Мой доктор':
                send_message_specialities.delay(message.from_user.id)

        if body.callback_query:
            message = body.callback_query
            logging.info(f'Incoming callback_query from: {message.from_user.id} '
                         f'{message.from_user.username}, {message.data}')
            try:
                data = json.loads(body.callback_query.data)
            except json.JSONDecodeError:
                logging.error(f'JSONDecodeError: {body.callback_query.data}')
                return HttpResponse(status=200)

            if data.get('type') == 'speciality':
                send_message_districts.delay(
                    message.from_user.id,
                    message.message.message_id,
                    data['data']
                )

            elif data.get('type') == 'district':
                speciality, district = map(lambda x: x.split('_')[1], data['data'].split(','))
                doctors = Doctor.objects.filter(speciality=speciality, district=district).all()
                if not doctors:
                    text = f'<i>{texts.no_doctors}</i>'
                    send_message('sendMessage', chat_id=message.from_user.id, parse_mode='HTML', text=text)
                else:
                    send_message('deleteMessage', chat_id=message.from_user.id, message_id=message.message.message_id)

                    for doctor in doctors:
                        send_message_doctor.delay(
                            message.from_user.id,
                            doctor.id
                        )

            elif data.get('type') == 'doctor':
                doctor = Doctor.objects.get(id=data['data'])
                send_message(
                    'sendContact',
                    chat_id=message.from_user.id,
                    phone_number=doctor.phone,
                    first_name=doctor.full_name
                )

        return HttpResponse(status=200)
    return HttpResponse(status=400)
