from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import json
from bot.misc import DotAccessibleDict
from bot.tasks import send_message_to_new_user, send_message_specialities, \
    send_message_districts, send_message_doctor, send_message_clinic_or_private, \
    send_message_polyclinic
from bot.models import User, Doctor, Speciality, Polyclinic
from bot.misc import send_message
from bot import texts


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST' and request.headers.get('X-Telegram-Bot-Api-Secret-Token') == settings.X_TELEGRAM_BOT_API_SECRET_TOKEN:
        body = json.loads(request.body)
        body = DotAccessibleDict(body)
        logging.info(f'\n{body}\n')
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
                send_message_clinic_or_private.delay(message.from_user.id, message.message.message_id, data['data'])

            if data.get('type') == 'clinic_or_private':
                send_message_districts.delay(message.from_user.id, message.message.message_id, data['data'])

            if data.get('type') == 'district':
                clinic_or_private, speciality_id, district_id = data['data'].split(',')
                speciality_id = int(speciality_id)
                district_id = int(district_id)

                if clinic_or_private == 'private':
                    result = []
                    doctors = Doctor.objects.prefetch_related('district').filter(speciality=speciality_id).all()
                    if doctors:
                        for doctor in doctors:
                            if list(filter(lambda x: x == district_id, [i.id for i in doctor.district.all()])):
                                result.append(doctor)

                    if result:
                        result = sorted(result, key=lambda x: int(x.rating) if x.rating else 10)
                        doctors_id = [i.id for i in result]
                        send_message_doctor.delay(message.from_user.id, message.message.message_id, doctors_id)
                    else:
                        send_message('sendMessage', chat_id=message.from_user.id, parse_mode='HTML', text=f'<i>{texts.no_doctors}</i>')

                elif clinic_or_private == 'clinic':
                    result = []
                    polyclinics = Polyclinic.objects.prefetch_related('speciality').filter(district__id=district_id).all()
                    if polyclinics:
                        for polyclinic in polyclinics:
                            if list(filter(lambda x: x == speciality_id, [i.id for i in polyclinic.speciality.all()])):
                                result.append(polyclinic)

                    if result:
                        result = sorted(result, key=lambda x: int(x.rating) if x.rating else 10)
                        polyclinics_id = [i.id for i in result]
                        send_message_polyclinic.delay(message.from_user.id, message.message.message_id, polyclinics_id)
                    else:
                        send_message('sendMessage', chat_id=message.from_user.id, parse_mode='HTML', text=f'<i>{texts.no_doctors}</i>')

        return HttpResponse(status=200)
    return HttpResponse(status=400)
