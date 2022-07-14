from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('postgresql://az_user:az_psw@db:5432/az_dbname')

"""
БД вынесено в отдельный файл для декомпозиции моделей
"""