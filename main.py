import requests
import json

BASE_URL = 'https://emias.info/api/emc/appointment-eip/v1/'
ENDPOINTS = {
    'SPECIALISTS_INFO': '?getAvailableResourceScheduleInfo',
    'DOCTORS_INFO': '?getDoctorsInfo',
    'DOCTOR_SCHEDULE': '?getAvailableResourceScheduleInfo',
    'CREATE_APPOINTMENTS': '?createAppointment',
    'GET_APPOINTMENT': '?getAppointmentReceptionsByPatient'

}
OMS_NUMBER = '3656100896000147'
BIRTH_DATE = '1998-03-03'
ID = 'RneyzJNzOMaglqe0KXcOK'

context_1 = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getSpecialitiesInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE
    }
}

context = {
    "jsonrpc": "2.0",
    "id": "WBi_CZivOTAOrVMgDSfMl",
    "method": "getAvailableResourceScheduleInfo",
    "params": {
        "omsNumber": "3656100896000147",
        "birthDate": "1998-03-03",
        "availableResourceId": 11161541,
        "complexResourceId": 10061900,
        "specialityId": "3"
    }
}

# url = BASE_URL + ENDPOINTS['SPECIALISTS_INFO']
# r = requests.post(url, json=context_1)
# z = r.text
# json_response = json.loads(z)
# print(json_response)
# print(type(z))

def get_available_specialists(context):
    url = BASE_URL + ENDPOINTS['SPECIALISTS_INFO']
    response = requests.post(url, json=context)
    data = response.text
    json_response = json.loads(data)
    specialist_dict = {}
    for _ in json_response['result']:
        try:
            specialist_dict[_['name']] = [_['code'], _['onlyByRefferal']]
        except KeyError:
            specialist_dict[_['name']] = [_['code'], False]
    return specialist_dict

specialities = get_available_specialists(context_1)
# print(specialities['Хирург'][0])


context_2 = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getDoctorsInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE,
        "specialityId": specialities['Физиотерапевт'][0],
        # "referralId" 121903232664
    }
}

context_21 = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getDoctorsInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE,
        "specialityId": specialities['Хирург'][0],
    }
}

def get_doctors_info(context, speciality_name, specialities):
    try:
        context['params'].pop('availableResourceId')
        context['params'].pop('complexResourceId')
    except KeyError:
        pass
    context['method'] = 'getDoctorsInfo'
    context['params']['specialityId'] = specialities[speciality_name][0]
    if specialities[speciality_name][1] == True:
        context['params']['referralId'] = 121903232664
    url = BASE_URL + ENDPOINTS['DOCTORS_INFO']
    response = requests.post(url, json=context)
    json_response = json.loads(response.text)
    doctors_dict = {}

    return json_response

z = get_doctors_info(context, 'Физиотерапевт', specialities)
print(z)

def get_doctor_schedule():
    pass

    
