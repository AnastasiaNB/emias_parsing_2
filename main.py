from parsing import (
    get_refferals, get_available_specialists,
    get_doctors_info, get_doctor_schedule,
    create_appointment
)
from json_templates import (
    get_specialists_info_json, get_doctor_info_json,
    get_doctor_schedule_json, create_appointment_json,
    get_refferals_json, create_template
)
from user_data import speciality_name, best_time, best_date
from tables import users
from database import engine
from sqlalchemy.exc import IntegrityError
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, TypeHandler
import os
from dotenv import load_dotenv
import json

user_data = {}
load_dotenv()

emias_parser_bot = Bot(token=os.getenv('BOT_TOKEN'))
emias_parser_update = Updater(token=os.getenv('BOT_TOKEN'))
user_data = {}

def send_help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Use this bot for creating appointments on EMIAS.info. For begin input /start"
    )

def send_welcome(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Welcome to EMIAS Parser. Input your OMS policy number."
    )
    return 1

def get_oms_number(update, context):
    oms_number = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Input your birth date as YYYY-MM-DD"
    )
    user_data['oms_number'] = oms_number
    return 2

def get_birth_date(update, context):
    birth_date = update.message.text
    user_data['birth_date'] = birth_date
    create_user = users.insert().values(
        oms_number = user_data['oms_number'],
        birth_date = user_data['birth_date']
    )
    get_user = users.select().where(
        users.c.oms_number==user_data['oms_number'],
        users.c.birth_date==user_data['birth_date']
    )
    conn = engine.connect()
    try:
        conn.execute(create_user)
    except IntegrityError:
        pass
    user_id = conn.execute(get_user).first()[0]
    user_data.clear()
    user_data['user_id'] = user_id
    conn.commit()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Input best date for creating appointment as YYYY-MM-DD"
    )
    return 3

def get_best_date(update, context):
    best_date = update.message.text
    user_data['best_date'] = best_date
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Input best time for creating appointment as HH:MM"
    )
    return 4

def skip_best_date(update, context):
    return 4

def get_best_time(update, context):
    best_time = update.message.text
    user_data['best_time'] = best_time
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "OMS Number: {}\n Best date: {}\n Best time: {}\n To confirm input OK".format(
            user_data['user_id'], user_data['best_date'], user_data['best_time']
        )
    )
    return 5

def skip_best_time(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "OMS Number: {}\nBest date: {}\nBest time: {}\nTo confirm input OK".format(
            user_data['user_id'], user_data['best_date'], user_data['best_time']
        )
    )
    return 5

def get_doctor_list(update, context):
    conn = engine.connect()
    user_id = user_data['user_id']
    birth_date = conn.execute(users.select().where(users.c.oms_number==user_id)).first()[1]
    conn.commit()
    get_reff_json = create_template(get_refferals_json, user_id, birth_date)
    get_refferals(get_reff_json, user_id)
    get_av_spec_json = create_template(get_specialists_info_json, user_id, birth_date)
    doctor_list = [json.loads(spec) for spec in get_available_specialists(get_av_spec_json)]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = doctor_list
    )
    return ConversationHandler.END




    
handler = ConversationHandler(
    entry_points=[CommandHandler('start', send_welcome)],
    states={
        1: [MessageHandler(Filters.regex(r'\d{16}'), get_oms_number)],
        2: [MessageHandler(Filters.regex(r'\d{4}-\d\d-\d\d'), get_birth_date)],
        3: [MessageHandler(Filters.regex(r'\d{4}-\d\d-\d\d'), get_best_date), CommandHandler('skip', skip_best_date)],
        4: [MessageHandler(Filters.regex(r'\d\d:\d\d'), get_best_time), CommandHandler('skip', skip_best_time)],
        5: [MessageHandler(Filters.regex(r'OK'), get_doctor_list)],
    },
    fallbacks=[]
)

emias_parser_update.dispatcher.add_handler(CommandHandler('help', send_help))
emias_parser_update.dispatcher.add_handler(handler)


emias_parser_update.start_polling()
emias_parser_update.idle()


# get_refferals(get_refferals_json)
# get_available_specialists(get_specialists_info_json)
# get_doctors_info(get_doctor_info_json, speciality_name)
# get_doctor_schedule(get_doctor_schedule_json, speciality_name)
# create_appointment(context=create_appointment_json, speciality_name=speciality_name, best_date=best_date, best_time=best_time)        
