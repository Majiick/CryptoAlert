import psycopg2
import sqlalchemy
import time

try:
    engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres')
except sqlalchemy.exc.OperationalError:
    time.sleep(5)
    engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres')


