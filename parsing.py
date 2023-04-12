import requests
import json
from datetime import datetime


from database import engine
from tables import refferals, doctors, specialities, schedule, doctor_schedule
from sqlalchemy.exc import IntegrityError
from funcs import find_nearest_date, find_nearest_time 


BASE_URL = 'https://emias.info/api/emc/appointment-eip/v1/'
ENDPOINTS = {
    'SPECIALISTS_INFO': '?getAvailableResourceScheduleInfo',
    'DOCTORS_INFO': '?getDoctorsInfo',
    'DOCTOR_SCHEDULE': '?getAvailableResourceScheduleInfo',
    'CREATE_APPOINTMENTS': '?createAppointment',
    'GET_REFFERALS': '?getReferralsInfo'
}


def get_refferals(context, oms_number):
    """
    Getting refferals
    """
    url = BASE_URL + ENDPOINTS['GET_REFFERALS']
    response = requests.post(url, json=context)
    data = response.text
    json_response = json.loads(data)
    print(json_response)
    conn = engine.connect()
    for _ in json_response['result']:
        create_refferal = refferals.insert().values(
            id = _['id'],
            user_id = oms_number,
            speciality_id = _['toDoctor']['specialityId']
        )
        try:
            conn.execute(create_refferal)
        except IntegrityError:
            pass
    conn.commit()


def get_available_specialists(context):
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


def get_doctors_info(context: dict, speciality_name):
    """
    Getting doctors for chosen speciality
    """
    select_spec = specialities.select().where(specialities.c.name == speciality_name)
    user_id = "3656100896000147" # get it from user table
    conn = engine.connect()
    speciality = conn.execute(select_spec).first()
    speciality_id = speciality[0]
    context['params']['specialityId'] = speciality_id
    if speciality[2] is True:
        refferal_id = conn.execute(refferals.select().where(refferals.c.user_id==user_id,refferals.c.speciality_id==speciality_id)).first()[0]
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


def get_doctor_schedule(context, speciality_name):
    """
    Getting available schedule
    """
    url = BASE_URL + ENDPOINTS['DOCTOR_SCHEDULE']
    conn = engine.connect()
    speciality_id = conn.execute(specialities.select().where(specialities.c.name==speciality_name)).first()[0]
    docs = conn.execute(doctors.select().where(doctors.c.speciality_id==speciality_id)).fetchall()
    for doc in docs:
        context['params']['specialityId'] = doc[3]
        context['params']['availableResourceId'] = doc[0]
        context['params']['complexResourceId'] = doc[2]
        speciality = conn.execute(specialities.select().where(specialities.c.code==doc[3])).first()
        if speciality[2] is True:
            user_id = "3656100896000147" # get from user table
            refferal_id = conn.execute(refferals.select().where(
                refferals.c.user_id==user_id,
                refferals.c.speciality_id==speciality[0]
            )).first()[0]
            context['params']['referralId'] = refferal_id
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
                
                schedule_id = conn.execute(schedule.select().where(schedule.c.start_time==datetime.fromisoformat(start_time))).first()[0]
                conn.execute(doctor_schedule.insert().values(
                    schedule_id=schedule_id,
                    doctor_id = doc[0]
                ))
    conn.commit()
    return 


def create_appointment(context,  speciality_name, best_date=None, best_time=None,):
    """
    Creating appointment by the best coincidence to nesessary date and time
    """
    conn = engine.connect()
    speciality_id = conn.execute(specialities.select().where(specialities.c.name==speciality_name)).first()[0]
    docs = conn.execute(doctors.select().where(doctors.c.speciality_id==speciality_id)).fetchall()
    docs_ids = [doc[0] for doc in docs]
    if best_time:
        time = find_nearest_time(best_date=best_date, best_time=best_time)
        schedule_item = conn.execute(schedule.select().where(schedule.c.start_time==time)).first()
    else:
        day = find_nearest_date(best_date)
        schedule_item = conn.execute(schedule.select().where(schedule.c.day==day)).first()
    schedule_id = schedule_item[0]
    start_time = '{}+03:00'.format(schedule_item[2].isoformat())
    end_time = '{}+03:00'.format(schedule_item[3].isoformat())
    select_doc_schedule_item = doctor_schedule.select().where(
        (doctor_schedule.c.schedule_id==schedule_id) &
        (doctor_schedule.c.doctor_id.in_(docs_ids))
    )
    doctor_id = conn.execute(select_doc_schedule_item).first()[0]
    doctor = conn.execute(doctors.select().where(doctors.c.id==doctor_id)).first()
    complex_id = doctor[2]
    receptionType = doctor[4]
    speciality_id = doctor[3]
    speciality = conn.execute(specialities.select().where(specialities.c.code==speciality_id)).first()
    context['params']['availableResourceId'] = doctor_id
    context['params']['complexResourceId'] = complex_id
    context['params']['specialityId'] = speciality_id
    context['params']['startTime'] = start_time
    context['params']['endTime'] = end_time
    if speciality[2] == True:
        user_id = "3656100896000147" # get from user table
        refferal_id = conn.execute(refferals.select().where(
            refferals.c.user_id==user_id,
            refferals.c.speciality_id==speciality_id
        )).first()[0]
        context['params']['referralId'] = refferal_id
    else:
        context['params']['receptionTypeId'] = receptionType
    url = BASE_URL + ENDPOINTS['CREATE_APPOINTMENTS']
    response = requests.post(url, json=context)
    if response.status_code == 200:
        conn.execute(doctor_schedule.delete())
        conn.execute(schedule.delete())
        conn.commit()

