from sqlalchemy import create_engine, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
import sqlalchemy as sa
import os

def conexao():
    server      = os.getenv("DB_HOST") 
    database    = os.getenv("DB_NAME")
    username    = os.getenv("DB_USER")
    password    = os.getenv("DB_PASSWORD")
    port        = os.getenv("DB_PORT")
    engine_postgres = sa.create_engine(f'postgresql+psycopg2://{username}:{password}@{server}:{port}/{database}')
    return engine_postgres

def create_session():
    engine = conexao()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
