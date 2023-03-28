from user_data import ID, OMS_NUMBER, BIRTH_DATE


get_specialists_info_json = {
    "jsonrpc": "2.0",
    "id": ID,
    "method": "getSpecialitiesInfo",
    "params": {
        "omsNumber": OMS_NUMBER,
        "birthDate": BIRTH_DATE
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
        # "availableResourceId": 13277127,
        # "complexResourceId": 10061897,
        # "receptionTypeId": "1913",
        # "specialityId": "3",
        # "startTime": "2023-04-05T13:20:00.000+03:00",
        # "endTime": "2023-04-05T13:40:00.000+03:00"
    }
}
