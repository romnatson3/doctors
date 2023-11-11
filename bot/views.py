from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from bot.misc import DotAccessibleDict
from bot.tasks import send_message_to_new_user, send_message_specialities, \
    send_message_districts, send_message_doctor, send_message_clinic_or_private, \
    send_message_polyclinic
from bot.models import User, Doctor, Speciality, Polyclinic
from bot.misc import send_message
from bot import texts
from django.db.models import Q


@csrf_exempt
def telegram_webhook(request):
    # if request.method == 'POST' and request.headers.get('X-Telegram-Bot-Api-Secret-Token') == settings.X_TELEGRAM_BOT_API_SECRET_TOKEN:
    if request.method == 'POST':
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
                send_message_clinic_or_private.delay(message.from_user.id)

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
                send_message_districts.delay(message.from_user.id, message.message.message_id, data['data'])

            if data.get('type') == 'clinic_or_private':
                send_message_specialities.delay(message.from_user.id, message.message.message_id, data['data'])

            if data.get('type') == 'district':
                clinic_or_private, speciality_id, district_id = data['data'].split(',')
                speciality_id = int(speciality_id)
                district_id = int(district_id)

                if clinic_or_private == 'private':
                    doctors_first = []
                    other_doctors = []
                    speciality = (Speciality.objects.select_related(
                        'rating_1', 'rating_2', 'rating_3', 'rating_4', 'rating_5')
                        .prefetch_related(
                            'rating_1__district', 'rating_2__district', 'rating_3__district',
                            'rating_4__district', 'rating_5__district')
                        .filter(id=speciality_id).first())

                    if speciality:
                        doctors_rating = [
                            speciality.rating_1, speciality.rating_2, speciality.rating_3,
                            speciality.rating_4, speciality.rating_5
                        ]
                        for doctor in doctors_rating:
                            if doctor:
                                district = list(filter(lambda x: x.id == district_id, doctor.district.all()))
                                if district and doctor not in doctors_first:
                                    doctors_first.append(doctor)

                        doctors_first_id = [i.id for i in doctors_first]
                        sql = Q(~Q(id__in=doctors_first_id) & Q(speciality=speciality_id) & Q(district=district_id))
                    else:
                        sql = Q(speciality=speciality_id) & Q(district=district_id)
                    other_doctors = Doctor.objects.filter(sql).all()

                    if not (doctors_first or other_doctors):
                        text = f'<i>{texts.no_doctors}</i>'
                        send_message('sendMessage', chat_id=message.from_user.id, parse_mode='HTML', text=text)
                    else:
                        doctors_id = [i.id for i in doctors_first + list(other_doctors)]
                        send_message_doctor.delay(message.from_user.id, message.message.message_id, doctors_id)

                elif clinic_or_private == 'clinic':
                    polyclinics_id = []
                    polyclinics = Polyclinic.objects.prefetch_related('speciality').filter(district__id=district_id).all()
                    if polyclinics:
                        for polyclinic in polyclinics:
                            if list(filter(lambda x: x == speciality_id, [i.id for i in polyclinic.speciality.all()])):
                                polyclinics_id.append(polyclinic.id)

                    if polyclinics_id:
                        send_message_polyclinic.delay(message.from_user.id, message.message.message_id, polyclinics_id)
                    else:
                        text = f'<i>{texts.no_doctors}</i>'
                        send_message('sendMessage', chat_id=message.from_user.id, parse_mode='HTML', text=text)

        return HttpResponse(status=200)
    return HttpResponse(status=400)
