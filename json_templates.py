

ID = 'Po65Xlo_f_8rJKBVHWJCW' # put to .env
OMS_NUMBER = '3656100896000147'
BIRTH_DATE = '1998-03-03'

get_specialists_info_json = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getSpecialitiesInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE
    }
}

get_refferals_json = {
    "jsonrpc": "2.0",
    "id": "XrvEZXHpaz4aXaxi7Hg4e",
    "method": "getReferralsInfo",
    "params": {
        "omsNumber": "3656100896000147",
        "birthDate": "1998-03-03"
    }
}

get_doctor_info_json = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getDoctorsInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE,
    }
}

get_doctor_schedule_json = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getAvailableResourceScheduleInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE,
    }
}

create_appointment_json = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "createAppointment",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE,
    }
}
