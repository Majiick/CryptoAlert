import psycopg2
import sqlalchemy
import time

try:
    engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres', pool_size=400, max_overflow=10)
except sqlalchemy.exc.OperationalError:
    time.sleep(5)
    engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres', pool_size=400, max_overflow=10)


