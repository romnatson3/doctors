import logging
import redis
import json
from celery.utils.log import get_task_logger
from teleredis import RedisSession
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.errors import FloodError
from django.conf import settings
from django.db.transaction import atomic
from django.core.cache import cache
from django.db.models.functions import Concat, Cast
from django.db.models import CharField, Value, F
from app.celery import app
from bot.models import User
from bot.misc import send_message, batched
from bot import texts
from bot.models import Speciality, District, Doctor, Polyclinic


logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)


@app.task(queue='schedule')
def get_users_count():
    chat_member_count = cache.get('chat_member_count', 0)
    current_chat_member_count = send_message('getChatMemberCount', chat_id=settings.TELEGRAM_CHANNEL_ID)
    cache.set('chat_member_count', current_chat_member_count)
    if current_chat_member_count != chat_member_count:
        logger.info(f'Chat member count: {current_chat_member_count}')
        get_users_from_channel.delay()
    else:
        logger.info(f'No new users. Chat member count: {current_chat_member_count}')


@app.task(
    bind=True,
    max_retries=1,
    default_retry_delay=10,
    queue='schedule'
)
def get_users_from_channel(self):
    try:
        new_users = []
        new_users_id = []
        users_in_chat_id = []
        enable_users_id = []

        users_in_chat = get_all_chat_users(int(settings.TELEGRAM_CHANNEL_ID))
        users = dict(User.objects.values_list('id', 'is_deleted').all())
        for user in users_in_chat:
            users_in_chat_id.append(user.id)
            if user.bot and not user.is_self:
                logger.warning(f'Some strange bot here: @{user.username}')

            if user.id not in users:
                new_users_id.append(user.id)
                logger.info(f'New user @{user.username}, id={user.id}')
                new_users.append(
                    User(id=user.id, username=user.username, first_name=user.first_name,
                         last_name=user.last_name, phone=user.phone, is_bot=user.bot)
                )

            if users.get(user.id) is False:
                enable_users_id.append(user.id)
                logger.info(f'Enable user @{user.username}, id={user.id}')

        with atomic():
            if new_users:
                User.objects.bulk_create(new_users)
                logger.info(f'Created {len(new_users)} users')
            if enable_users_id:
                enabled = User.objects.filter(id__in=enable_users_id).update(is_deleted=False)
                logger.info(f'Enabled {enabled} users')
            deleted = User.objects.exclude(id__in=users_in_chat_id).update(is_deleted=True)
            logger.info(f'Deleted {deleted} users')

        for user_id in new_users_id + enable_users_id:
            send_message_to_new_user.delay(user_id)

    except FloodError as e:
        logger.error(f'Error: {e}')
        raise e
    except Exception as e:
        logger.error(f'Error: {e}')
        raise self.retry(exc=e)


def get_all_chat_users(chat_id):
    redis_connector = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2, decode_responses=False)
    redis_session = RedisSession('client', redis_connector)
    client = TelegramClient(redis_session, settings.APP_API_ID, settings.APP_API_HASH)
    # client.session.save_entities = False
    client.start(bot_token=settings.TELEGRAM_TOKEN)
    all_users = []
    with client:
        chat = client.get_entity(chat_id)
        limit = 100
        index = 0
        while True:
            users = client(GetParticipantsRequest(
                chat, filter=chat,
                offset=index * limit, limit=limit, hash=0)
            ).users
            if not users:
                break
            all_users.extend(users)
            index += 1
    return all_users


@app.task()
def send_message_to_new_user(id):
    text = f'<b>{texts.start}</b>'
    reply_markup = json.dumps({'keyboard': [[{'text': 'Мой доктор'}]], 'resize_keyboard': True})
    send_message('sendMessage', chat_id=id, parse_mode='HTML', text=text, reply_markup=reply_markup)
    logger.info(f'Send start message to {id=} successfully')


@app.task()
def send_message_specialities(id):
    specialities = Speciality.objects.annotate(
        text=F('name'),
        callback_data=Concat(
            Value('{"type":"speciality","data":"'),
            Cast(F('id'), output_field=CharField()),
            Value('"}')
        )
    ).values('text', 'callback_data').order_by('name')
    text = f'<b>{texts.my_doctor}</b>'
    inline_keyboard = batched(specialities, 2)
    reply_markup = json.dumps({'inline_keyboard': inline_keyboard})
    send_message('sendMessage', chat_id=id, parse_mode='HTML', text=text, reply_markup=reply_markup)
    logger.info(f'Send message about specialities to {id=} successfully')


@app.task()
def send_message_clinic_or_private(id, message_id, previous_callback_data):
    clinic_callback_data = json.dumps({'type': 'clinic_or_private', 'data': f'{previous_callback_data},clinic'})
    private_callback_data = json.dumps({'type': 'clinic_or_private', 'data': f'{previous_callback_data},private'})
    inline_keyboard = [[
        {'text': texts.clinic, 'callback_data': clinic_callback_data},
        {'text': texts.private, 'callback_data': private_callback_data}
    ]]
    reply_markup = json.dumps({'inline_keyboard': inline_keyboard})
    text = f'<b>{texts.clinic_or_private}</b>'
    send_message('editMessageText', chat_id=id, message_id=message_id, reply_markup=reply_markup, text=text, parse_mode='HTML')
    logger.info(f'Send message about clinic or private to {id=} successfully')


@app.task()
def send_message_districts(id, message_id, previous_callback_data):
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
    send_message('editMessageText', chat_id=id, message_id=message_id, reply_markup=reply_markup, text=text, parse_mode='HTML')
    logger.info(f'Send message about districts to {id=} successfully')


@app.task()
def send_message_doctor(id, doctors_id):
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
        caption = fullname + speciality + position + polyclinics + experience + cost + schedules
        callback_data = json.dumps({'type': 'doctor_contacts', 'data': doctor.id})
        reply_markup = json.dumps({'inline_keyboard': [[{'text': texts.get_contact, 'callback_data': callback_data}]]})
        send_message('sendPhoto', chat_id=id, parse_mode='HTML', caption=caption, reply_markup=reply_markup, photo=doctor.image.path)
        logger.info(f'Send message about doctor to {id=} successfully')


@app.task()
def send_message_polyclinic(id, polyclinics_id):
    polyclinics = list(Polyclinic.objects.select_related('district')
                       .prefetch_related('phone', 'speciality', 'position')
                       .filter(id__in=polyclinics_id).all())
    for polyclinic in polyclinics:
        name = f'<b>{polyclinic.name}\n</b>'
        address = f'{polyclinic._meta.get_field("address").verbose_name}: <i>{polyclinic.address}</i>\n'
        url = polyclinic.site_url if polyclinic.site_url else '-'
        site = f'{polyclinic._meta.get_field("site_url").verbose_name}: <a href="{url}">{url}</a>\n'
        work_time = f'{polyclinic.work_time.short_description}: <i>{polyclinic.work_time()}</i>\n'
        caption = name + address + site + work_time
        callback_data = json.dumps({'type': 'clinic_contacts', 'data': polyclinic.id})
        reply_markup = json.dumps({'inline_keyboard': [[{'text': texts.get_contact, 'callback_data': callback_data}]]})
        send_message('sendPhoto', chat_id=id, parse_mode='HTML', caption=caption, reply_markup=reply_markup, photo=polyclinic.image.path)
        logger.info(f'Send message about polyclinic to {id=} successfully')
