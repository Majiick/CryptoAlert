import sqlalchemy
import psycopg2
import time

file = open('postgresql_init.sql')
engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres')
escaped_sql = sqlalchemy.text(file.read())

try:
    engine.execute(escaped_sql)
except sqlalchemy.exc.OperationalError:
    time.sleep(2)  # Wait for postgres to startup.
    engine.execute(escaped_sql)
