import logging
import json
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from bot.misc import DotAccessibleDict
from bot.tasks import send_message_to_new_user, send_message_specialities, \
    send_message_districts, send_message_doctor, send_message_clinic_or_private, \
    send_message_polyclinic, send_message_before_searching, send_message_not_found, \
    send_message_not_found_share
from bot.models import User, Doctor, Polyclinic, Speciality
from bot import texts


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST' and request.headers.get('X-Telegram-Bot-Api-Secret-Token') == settings.X_TELEGRAM_BOT_API_SECRET_TOKEN:
        try:
            body = json.loads(request.body)
            body = DotAccessibleDict(body)
            logging.info(f'\n{body}\n')
        except Exception as e:
            logging.error('Error while parsing request body. Body:{request.body}')
            logging.exception(e)
            return HttpResponse(status=200)

        # return HttpResponse(status=200)

        if body.message.text:
            message = body.message
            logging.info(f'Incoming message from: {message.from_user.id} {message.from_user.username}, {message.text}')

            search_request = cache.get(f'{message.from_user.id}_search_request')

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

            elif message.text == texts.my_doctor_button:
                send_message_specialities.delay(message.from_user.id)

            elif message.text == texts.search_by_speciality_button:
                cache.set(f'{message.from_user.id}_search_request', True, timeout=3600)
                send_message_before_searching(message.from_user.id)

            elif message.text == texts.share:
                where = Q(
                    ~Q(share__id=None) &
                    # Q(share__start_date__lte=datetime.today().date()) &
                    Q(share__end_date__gte=datetime.today().date())
                )
                polyclinics = Polyclinic.objects.filter(where).values('id', 'rating_share')
                if polyclinics:
                    polyclinics = sorted(polyclinics, key=lambda x: int(x['rating_share']) if x['rating_share'] else 10, reverse=True)
                    polyclinics_id = [i['id'] for i in polyclinics]
                    send_message_polyclinic.delay(message.from_user.id, None, polyclinics_id)
                else:
                    send_message_not_found_share.delay(id=message.from_user.id)

            elif search_request and len(message.text) >= 3:
                logging.info(f'User {message.from_user.id} searching by speciality: {message.text}')
                speciality_id = Speciality.objects.filter(name__icontains=message.text).values_list('id', flat=True)
                send_message_specialities.delay(message.from_user.id, list(speciality_id))

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
                    doctors = Doctor.objects.filter(district__id=district_id, speciality=speciality_id).values('id', 'rating_general')
                    if doctors:
                        doctors = sorted(doctors, key=lambda x: int(x['rating_general']) if x['rating_general'] else 10, reverse=True)
                        doctors_id = [i['id'] for i in doctors]
                        send_message_doctor.delay(message.from_user.id, message.message.message_id, doctors_id)
                    else:
                        send_message_not_found(id=message.from_user.id)

                elif clinic_or_private == 'clinic':
                    polyclinics = Polyclinic.objects.filter(speciality__id=speciality_id, district=district_id).values('id', 'rating_general')
                    if polyclinics:
                        polyclinics = sorted(polyclinics, key=lambda x: int(x['rating_general']) if x['rating_general'] else 10, reverse=True)
                        polyclinics_id = [i['id'] for i in polyclinics]
                        send_message_polyclinic.delay(message.from_user.id, message.message.message_id, polyclinics_id)
                    else:
                        send_message_not_found(id=message.from_user.id)

        return HttpResponse(status=200)
    return HttpResponse(status=400)
