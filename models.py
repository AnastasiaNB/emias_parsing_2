from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

from fastapi import FastAPI
 
SQLALCHEMY_DATABASE_URL = "sqlite:///./emias_parser_data.db"
 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base = declarative_base()

class Speciality(Base):
    __tablename__ = 'specialities'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    code: Mapped[int] = mapped_column(Integer)
    onlyByRefferal: Mapped[bool] = mapped_column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

emias_parser = FastAPI()
