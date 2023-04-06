from sqlalchemy import create_engine

from tables import metadata
 
SQLALCHEMY_DATABASE_URL = "sqlite:///./emias_parser_data.db"
 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

