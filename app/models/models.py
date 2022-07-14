import string
import random

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
engine = create_engine('postgresql://az_user:az_psw@db:5432/az_dbname')
Base = declarative_base()
Base.metadata.reflect(engine)

class Movie(Base):
    """
    Пример модели для работы с базой данныз
    """
    __table__ = Base.metadata.tables['movies']

class Rating(Base):

    __table__ = Base.metadata.tables['ratings']

class Links(Base):

    __table__ = Base.metadata.tables['links']

# class Recommendations(Base):

#     __table__ = Base.metadata.tables['recommendations']