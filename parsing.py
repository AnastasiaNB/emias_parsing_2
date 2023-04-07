import requests
import json
from datetime import datetime, date, time, timedelta

from json_templates import get_specialists_info_json, get_doctor_info_json, get_doctor_schedule_json, create_appointment_json, get_refferals_json
from user_data import speciality_name, best_time, best_date
from database import engine
from tables import users, refferals, appointments, doctors, specialities, schedule, doctor_schedule
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update


BASE_URL = 'https://emias.info/api/emc/appointment-eip/v1/'
ENDPOINTS = {
    'SPECIALISTS_INFO': '?getAvailableResourceScheduleInfo',
    'DOCTORS_INFO': '?getDoctorsInfo',
    'DOCTOR_SCHEDULE': '?getAvailableResourceScheduleInfo',
    'CREATE_APPOINTMENTS': '?createAppointment',
    'GET_REFFERALS': '?getReferralsInfo'
}


def get_refferals(context):
    """
    Getting refferals
    """
    url = BASE_URL + ENDPOINTS['GET_REFFERALS']
    response = requests.post(url, json=context)
    data = response.text
    json_response = json.loads(data)
    conn = engine.connect()
    for _ in json_response['result']:
        create_refferal = refferals.insert().values(
            id = _['id'],
            user_id = "3656100896000147", # get it from user table
            speciality_id = _['toDoctor']['specialityId']
        )
        try:
            conn.execute(create_refferal)
        except IntegrityError:
            pass
    conn.commit()

a = get_refferals(get_refferals_json)

def get_available_specialists(context: dict):
    """
    Getting available specialities
    """
    url = BASE_URL + ENDPOINTS['SPECIALISTS_INFO']
    response = requests.post(url, json=context)
    data = response.text
    json_response = json.loads(data)
    conn = engine.connect()
    for _ in json_response['result']:
        try:
            onlyByRefferal = _['onlyByRefferal']
        except KeyError:
            onlyByRefferal = False
        insert_spec = specialities.insert().values(
                name = _['name'],
                code = int(_['code']),
                onlyByRefferal = onlyByRefferal
            )
        try:
            conn.execute(insert_spec)
        except IntegrityError:
            pass
    conn.commit()
    select_spec = specialities.select()
    spec_names = []
    spec_list = conn.execute(select_spec)
    for spec in spec_list:
        spec_names.append(spec[1])
    return spec_names 

SPECIALITIES_DICT = get_available_specialists(get_specialists_info_json)

def get_doctors_info(context: dict, speciality_name):
    """
    Getting doctors for chosen speciality
    """
    select_spec = specialities.select().where(specialities.c.name == speciality_name)
    user_id = context['params']['omsNumber'], # get it from user table
    conn = engine.connect()
    speciality = conn.execute(select_spec).first()
    speciality_id = speciality[0]
    refferal_id = conn.execute(refferals.select().where(
        refferals.c.user_id==user_id,
        refferals.c.speciality_id==speciality_id
    )).first()[0]
    context['params']['specialityId'] = speciality_id
    if speciality[2] is True:
        context['params']['referralId'] = refferal_id
    url = BASE_URL + ENDPOINTS['DOCTORS_INFO']
    response = requests.post(url, json=context)
    json_response = json.loads(response.text)
    for _ in json_response['result']:
        insert_doc = doctors.insert().values(
                speciality_id = _['arSpecialityId'],
                id = _['id'],
                complex_id = _['complexResource'][0]['id'],
                name = _['name'],
                receptionType = _['receptionType'][0]['code'] 
            )
        try:
            conn.execute(insert_doc)
        except IntegrityError:
            pass
    conn.commit()
    return 


DOCTORS_DICT = get_doctors_info(get_doctor_info_json, 'Физиотерапевт')

def get_doctor_schedule(context):
    """
    Getting available schedule
    """
    url = BASE_URL + ENDPOINTS['DOCTOR_SCHEDULE']
    conn = engine.connect()
    docs = conn.execute(doctors.select()).fetchall()
    for doc in docs:
        context['params']['specialityId'] = doc[3]
        context['params']['availableResourceId'] = doc[0]
        context['params']['complexResourceId'] = doc[2]
        response = requests.post(url, json=context)
        json_response = json.loads(response.text)
        for _ in json_response['result']['scheduleOfDay']:
            day = _['date']
            possible_times = _['scheduleBySlot'][0]['slot']
            for time in possible_times:
                start_time = time['startTime']
                end_time = time['endTime']
                insert_time = schedule.insert().values(
                    day = day,
                    start_time = datetime.fromisoformat(start_time),
                    end_time = datetime.fromisoformat(end_time)
                )
                try:
                    conn.execute(insert_time)
                except IntegrityError:
                    pass
                
                schedule_id = conn.execute(schedule.select()).fetchall()[-1][0]
                conn.execute(doctor_schedule.insert().values(
                    schedule_id=schedule_id,
                    doctor_id = doc[0]
                ))
    conn.commit()
    return 

SCHEDULE_DICT = get_doctor_schedule(get_doctor_schedule_json)

def find_nearest_date(best_date):
    conn = engine.connect()
    select_best_day = schedule.select().where(schedule.c.day==best_date)
    times = conn.execute(select_best_day)
    if times.fetchall() == []:
        select_unique_day = schedule.select().group_by('day')
        days = [date.fromisoformat(day[1]) for day in conn.execute(select_unique_day).fetchall()]
        best_iso = date.fromisoformat(best_date)
        best_date = min(days, key = lambda x: abs(best_iso - x))
        return best_date
    return best_date

def find_nearest_time(best_time, best_date = None):
    conn = engine.connect()
    if best_date:
        date = '{}T{}:00'.format(best_date, best_time)
        iso_date = datetime.fromisoformat(date)
        select_best_day = schedule.select().where(schedule.c.day==best_date)
        start_times = [day[2] for day in conn.execute(select_best_day).fetchall()]
        best_time = min(start_times, key = lambda x: abs(iso_date - x))
        return best_time
    start_times = [day[2] for day in conn.execute(schedule.select()).fetchall()]
    time_iso = time.fromisoformat('{}:00'.format(best_time))
    best_time = min(start_times, key = lambda x: abs(
        timedelta(hours=time_iso.hour, minutes=time_iso.minute) - timedelta(hours=x.hour, minutes=x.minute)))
    return best_time


def create_appointment(context, best_date=None, best_time=None):
    """
    Creating appointment by the best coincidence to nesessary date and time
    """
    conn = engine.connect()
    if best_time:
        time = find_nearest_time(best_date=best_date, best_time=best_time)
        schedule_item = conn.execute(schedule.select().where(schedule.c.start_time==time)).first()
    else:
        day = find_nearest_date(best_date)
        schedule_item = conn.execute(schedule.select().where(schedule.c.day==day)).first()
    schedule_id = schedule_item[0]
    start_time = '{}+03:00'.format(schedule_item[2].isoformat())
    end_time = '{}+03:00'.format(schedule_item[3].isoformat())
    select_doc_schedule_item = doctor_schedule.select().where(doctor_schedule.c.schedule_id==schedule_id)
    doctor_id = conn.execute(select_doc_schedule_item).first()[0]
    doctor = conn.execute(doctors.select().where(doctors.c.id==doctor_id)).first()
    complex_id = doctor[2]
    receptionType = doctor[4]
    speciality_id = doctor[3]
    context['params']['availableResourceId'] = doctor_id
    context['params']['complexResourceId'] = complex_id
    context['params']['receptionTypeId'] = receptionType
    context['params']['specialityId'] = speciality_id
    context['params']['startTime'] = start_time
    context['params']['endTime'] = end_time
    url = BASE_URL + ENDPOINTS['CREATE_APPOINTMENTS']
    response = requests.post(url, json=context)
    data = response.text
    json_response = json.loads(data)
    appointment_id = json_response['result']['appointmentId']
    if response.status_code == 200:
        create_appointment = appointments.insert().values(
            id = appointment_id,
            time = schedule_id,
            user_id = context['params']['omsNumber'], # get it from user table
            doctor_id = doctor_id
        )
        conn.execute(create_appointment)
        conn.commit()

                
        # print(context)
# a = create_appointment(context=create_appointment_json, best_date=best_date, best_time=best_time)        



    
# create_appointment(create_appointment_json, SCHEDULE_DICT, best_time=best_time)

