from dotenv import load_dotenv
import os

load_dotenv()

get_specialists_info_json = {
    "jsonrpc": "2.0",
    "id": os.getenv('ID'),
    "method": "getSpecialitiesInfo",
    "params": {
        "omsNumber": "OMS_NUMBER",
        "birthDate": "BIRTH_DATE"
    }
}

get_refferals_json = {
    "jsonrpc": "2.0",
    "id": os.getenv('ID'),
    "method": "getReferralsInfo",
    "params": {
        "omsNumber": "OMS_NUMBER",
        "birthDate": "BIRTH_DATE"
    }
}

get_doctor_info_json = {
    "jsonrpc": "2.0",
    "id": os.getenv('ID'),
    "method": "getDoctorsInfo",
    "params": {
        "omsNumber": "OMS_NUMBER",
        "birthDate": "BIRTH_DATE",
    }
}

get_doctor_schedule_json = {
    "jsonrpc": "2.0",
    "id": os.getenv('ID'),
    "method": "getAvailableResourceScheduleInfo",
    "params": {
        "omsNumber": "OMS_NUMBER",
        "birthDate": "BIRTH_DATE",
    }
}

create_appointment_json = {
    "jsonrpc": "2.0",
    "id": os.getenv('ID'),
    "method": "createAppointment",
    "params": {
        "omsNumber": "OMS_NUMBER",
        "birthDate": "BIRTH_DATE",
    }
}

def create_template(template, oms_number, birth_date):
    template['params']['omsNumber'] = oms_number
    template['params']['birthDate'] = birth_date
    return template