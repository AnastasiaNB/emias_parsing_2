from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, MetaData, Table


metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('oms_number', Integer, primary_key=True),
    Column('birth_date', String)
)
   


refferals = Table(
    'refferals',
    metadata,
    Column('id', Integer, unique=True),
    Column('user_id', Integer, ForeignKey('users.oms_number')),
    Column('speciality_id', Integer, ForeignKey('specialities.code'))
)


specialities = Table(
    'specialities',
    metadata,
    Column('code', Integer, primary_key=True, unique=True),
    Column('name', String),
    Column('onlyByRefferal', Boolean, default=False)
)

doctors = Table(
    'doctors',
    metadata,
    Column('id', Integer, primary_key=True, unique=True),
    Column('name', String),
    Column('complex_id', Integer),
    Column('speciality_id', Integer, ForeignKey('specialities.code')),
    Column('schedule_id', Integer, ForeignKey('schedule.id'), nullable=True),
)


schedule = Table(
    'schedule',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('day', String),
    Column('start_time', TIMESTAMP),
    Column('end_time', TIMESTAMP),
)


appointments = Table(
    'appointments',
    metadata,
    Column('id', Integer, primary_key=True, unique=True),
    Column('time', Integer, ForeignKey('schedule.id')),
    Column('user_id', Integer, ForeignKey('users.oms_number')),
    Column('doctor_id', Integer, ForeignKey('doctors.id'))
)