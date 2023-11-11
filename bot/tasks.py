import logging
import json
from celery.utils.log import get_task_logger
from django.db.models.functions import Concat, Cast
from django.db.models import CharField, Value, F
from app.celery import app
from bot.misc import send_message, batched
from bot import texts
from bot.models import Speciality, District, Doctor, Polyclinic


logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)


@app.task()
def send_message_to_new_user(id):
    text = f'{texts.start}'
    reply_markup = json.dumps({'keyboard': [[{'text': 'Мой доктор'}]], 'resize_keyboard': True})
    send_message('sendMessage', chat_id=id, parse_mode='HTML', text=text, reply_markup=reply_markup)
    logger.info(f'Send start message to {id=} successfully')


@app.task()
def send_message_clinic_or_private(id):
    clinic_callback_data = json.dumps({'type': 'clinic_or_private', 'data': 'clinic'})
    private_callback_data = json.dumps({'type': 'clinic_or_private', 'data': 'private'})
    inline_keyboard = [[
        {'text': texts.clinic, 'callback_data': clinic_callback_data},
        {'text': texts.private, 'callback_data': private_callback_data}
    ]]
    reply_markup = json.dumps({'inline_keyboard': inline_keyboard})
    text = f'<b>{texts.clinic_or_private}</b>'
    send_message('sendMessage', chat_id=id, parse_mode='HTML', text=text, reply_markup=reply_markup)
    logger.info(f'Send message about clinic or private to {id=} successfully')


@app.task()
def send_message_specialities(id, message_id, previous_callback_data):
    specialities = Speciality.objects.annotate(
        text=F('name'),
        callback_data=Concat(
            Value('{"type":"speciality","data":"'),
            Value(f'{previous_callback_data},'),
            Cast(F('id'), output_field=CharField()),
            Value('"}')
        )
    ).values('text', 'callback_data').order_by('name')
    text = f'<b>{texts.my_doctor}</b>'
    inline_keyboard = batched(specialities, 2)
    reply_markup = json.dumps({'inline_keyboard': inline_keyboard})
    send_message('editMessageText', chat_id=id, message_id=message_id, reply_markup=reply_markup, text=text, parse_mode='HTML')
    logger.info(f'Send message about specialities to {id=} successfully')


@app.task()
def send_message_districts(id, message_id, previous_callback_data):
    send_message('deleteMessage', chat_id=id, message_id=message_id)
    specialities = District.objects.annotate(
        text=F('name'),
        callback_data=Concat(
            Value('{"type":"district","data":"'),
            Value(f'{previous_callback_data},'),
            Cast(F('id'), output_field=CharField()),
            Value('"}')
        )
    ).values('text', 'callback_data')
    text = f'<b>{texts.district}</b>'
    inline_keyboard = batched(specialities, 3)
    reply_markup = json.dumps({'inline_keyboard': inline_keyboard})
    send_message('sendMessage', chat_id=id, parse_mode='HTML', text=text, reply_markup=reply_markup)
    logger.info(f'Send message about districts to {id=} successfully')


@app.task()
def send_message_doctor(id, message_id, doctors_id):
    send_message('deleteMessage', chat_id=id, message_id=message_id)
    doctors = list(Doctor.objects
                   .select_related('speciality', 'position')
                   .prefetch_related('polyclinic', 'schedule')
                   .filter(id__in=doctors_id).all())
    doctors.sort(key=lambda x: doctors_id.index(x.id))
    for doctor in doctors:
        fullname = f'<b>{doctor.full_name}\n</b>'
        speciality = f'{doctor.speciality._meta.verbose_name}: <i>{doctor.speciality.name}\n</i>'
        position = f'{doctor.position._meta.verbose_name}: <i>{doctor.position.name}\n</i>'
        polyclinics = f'{doctor.polyclinic.model._meta.verbose_name_plural}:\n'
        for i in doctor.polyclinic.all():
            polyclinics += f'<i>{i.name} ({i.address})</i>\n'
        experience = f'{doctor._meta.get_field("experience").verbose_name}: <i>{doctor.experience} лет</i>\n'
        cost = f'{doctor._meta.get_field("cost").verbose_name}: <i>{doctor.cost} грн.</i>\n'
        schedules = f'{doctor.schedule.model._meta.verbose_name}:\n'
        for i in doctor.schedule.all():
            schedules += f'<i>{i.day_of_week_name} {i.start_time}-{i.end_time} - {i.polyclinic.name}</i>\n'
        phone = f'{doctor._meta.get_field("phone").verbose_name}:\n <i>{doctor.phone}</i>\n'
        caption = fullname + speciality + position + polyclinics + experience + cost + schedules + phone
        send_message('sendPhoto', chat_id=id, parse_mode='HTML', caption=caption, photo=doctor.image.path)
        logger.info(f'Send message about doctor to {id=} successfully')


@app.task()
def send_message_polyclinic(id, message_id, polyclinics_id):
    send_message('deleteMessage', chat_id=id, message_id=message_id)
    polyclinics = list(Polyclinic.objects.select_related('district')
                       .prefetch_related('phone', 'speciality', 'position')
                       .filter(id__in=polyclinics_id).all())
    for polyclinic in polyclinics:
        name = f'<b>{polyclinic.name}\n</b>'
        address = f'{polyclinic._meta.get_field("address").verbose_name}: <i>{polyclinic.address}</i>\n'
        url = polyclinic.site_url if polyclinic.site_url else '-'
        site = f'{polyclinic._meta.get_field("site_url").verbose_name}: <a href="{url}">{url}</a>\n'
        work_time = f'{polyclinic.work_time.short_description}: <i>{polyclinic.work_time()}</i>\n'
        phones = f'{polyclinic.phone.model._meta.verbose_name_plural}:\n'
        for phone in polyclinic.phone.all():
            phones += f'<i>{phone.number}</i>\n'
        caption = name + address + site + work_time + phones
        send_message('sendPhoto', chat_id=id, parse_mode='HTML', caption=caption, photo=polyclinic.image.path)
        logger.info(f'Send message about polyclinic to {id=} successfully')
