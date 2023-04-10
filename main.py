from parsing import (
    get_refferals, get_available_specialists,
    get_doctors_info, get_doctor_schedule,
    create_appointment
)
from json_templates import (
    get_specialists_info_json, get_doctor_info_json,
    get_doctor_schedule_json, create_appointment_json,
    get_refferals_json
)
from user_data import speciality_name, best_time, best_date
from tables import users
from database import engine
from sqlalchemy.exc import IntegrityError
from telethon import TelegramClient

emias_parser_bot = telebot.TeleBot('6174521988:AAEe8UXwSAw511WQx_7BqfBpdKKSv8mKOGE') # put token to .env

@emias_parser_bot.message_handler(commands=['help'])
def send_welcome(message):
    emias_parser_bot.reply_to(
        message,
        """Use this bot to create appointments on EMIAS. To start using input /start."""
    )

@emias_parser_bot.message_handler(commands=['start'])
def start(message):
    emias_parser_bot.send_message(message.from_user.id, "Intup your OMS policy number.")
    emias_parser_bot.register_next_step_handler(message, get_oms_number)

def get_oms_number(message):
    oms_number = message.text
    emias_parser_bot.send_message(message.from_user.id, 'Input your birth date as YYYY-MM-DD')
    emias_parser_bot.register_next_step_handler(message, get_birth_date)

def get_birth_date(message):
    birth_date = message.text
    # create_user = users.insert().values(
    #     oms_number = oms_number,
    #     birth_date = birth_date
    # )
    # get_user = users.select().where(
    #     users.c.oms_number==oms_number,
    #     users.c.birth_date==birth_date
    # )
    # conn = engine.connect()
    # try:
    #     conn.execute(create_user)
    # except IntegrityError:
    #     pass
    # user_id = conn.execute(get_user).first()
    # conn.commit()
    emias_parser_bot.send_message(message.from_user.id, "User created with oms {} bday {}".format(oms_number, birth_date))
#     emias_parser_bot.register_next_step_handler(message, user_id, get_json_templates)

# def get_json_templates(message, user_id):
#     pass

emias_parser_bot.infinity_polling()


# get_refferals(get_refferals_json)
# get_available_specialists(get_specialists_info_json)
# get_doctors_info(get_doctor_info_json, speciality_name)
# get_doctor_schedule(get_doctor_schedule_json, speciality_name)
# create_appointment(context=create_appointment_json, speciality_name=speciality_name, best_date=best_date, best_time=best_time)        
