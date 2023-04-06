import requests
import json
from datetime import datetime, date, time

from json_templates import get_specialists_info_json, get_doctor_info_json, get_doctor_schedule_json, create_appointment_json
from user_data import speciality_name, best_time, best_date
from database import engine
from tables import users, refferals, appointments, doctors, specialities, schedule
from sqlalchemy.exc import IntegrityError


BASE_URL = 'https://emias.info/api/emc/appointment-eip/v1/'
ENDPOINTS = {
    'SPECIALISTS_INFO': '?getAvailableResourceScheduleInfo',
    'DOCTORS_INFO': '?getDoctorsInfo',
    'DOCTOR_SCHEDULE': '?getAvailableResourceScheduleInfo',
    'CREATE_APPOINTMENTS': '?createAppointment',
    'GET_APPOINTMENT': '?getAppointmentReceptionsByPatient'

}

def get_available_specialists(context: dict):
    """
    Getting available doctors specialities
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
    Getting doctor list for chosen speciality
    """
    select_spec = specialities.select().where(specialities.c.name == speciality_name)
    conn = engine.connect()
    speciality = conn.execute(select_spec).first()
    context['params']['specialityId'] = speciality[0]
    if speciality[2] is True:
        context['params']['referralId'] = 121903232664  # def get_refferals_id()
    url = BASE_URL + ENDPOINTS['DOCTORS_INFO']
    response = requests.post(url, json=context)
    json_response = json.loads(response.text)
    for _ in json_response['result']:
        insert_doc = doctors.insert().values(
                speciality_id = _['arSpecialityId'],
                id = _['id'],
                complex_id = _['complexResource'][0]['id'],
                name = _['name']
            )
        try:
            conn.execute(insert_doc)
        except IntegrityError:
            pass
    conn.commit()
    return 


DOCTORS_DICT = get_doctors_info(get_doctor_info_json, 'Хирург')

def get_doctor_schedule(context):
    """
    Getting schedule for doctors in doctor list
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
    conn.commit()
        # schedule_dict[name] = {
        #     'specialityId': ids[0],
        #     'availableResourceId': ids[1],
        #     'complexResourceId': ids[2],
        #     'receptionTypeId': json_response['result']['availableResource']['receptionType'][0]['code'],
        #     'schedule': datetime_dict,
        #     }
    return 

SCHEDULE_DICT = get_doctor_schedule(get_doctor_schedule_json)
# print(SCHEDULE_DICT) 

def find_nearest_date(doctor_data, best_date):
    best_iso = date.fromisoformat(best_date)
    try:
        possible_time_list = doctor_data['schedule'][best_date]
    except KeyError:
        possible_date_list = [date.fromisoformat(_) for _ in doctor_data['schedule'].keys()]
        nearest_date = min(possible_date_list, key=lambda x: abs(x-best_iso))
        possible_time_list = doctor_data['schedule'][str(nearest_date)]
    return possible_time_list

def find_nearest_time(doctor_data, best_time):
    best_iso = time.fromisoformat(best_time)
    start_end_time_list = doctor_data['schedule'].values()
    possible_time_list = []
    for times in start_end_time_list:
        for t in times:
            if best_iso == t[0].time():
                return t
            possible_time_list.append(t[0].time)
        
    # nearest_time = 
            




    


def create_appointment(context, schedule_dict, best_date=None, best_time=None):
    """
    Creating appointment by the best coincidence to nesessary date and time
    """
    if best_date and best_time:
        best_iso = datetime.fromisoformat(best_date + 'T' + best_time + ':00')
    for doctor_data in schedule_dict.values():
        if best_date and best_time:
            pass
        elif best_date:
            possible_time_list = find_nearest_date(doctor_data, best_date)
            context['startTime'], context['endTime'] = possible_time_list[0][0], possible_time_list[0][1]
        elif best_time:
            find_nearest_time(doctor_data, best_time)


                
        # print(context)
        



    
# create_appointment(create_appointment_json, SCHEDULE_DICT, best_time=best_time)

