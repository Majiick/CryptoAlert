import sqlalchemy
import psycopg2
import time
from sqlalchemy.sql import text

file = open('postgresql_init.sql')
engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres')
escaped_sql = sqlalchemy.text(file.read())

try:
    engine.execute(escaped_sql)
except sqlalchemy.exc.OperationalError:
    time.sleep(5)  # Wait for postgres to startup.
    engine.execute(escaped_sql)

with engine.begin() as conn:
    try:
        conn.execute("insert into REGISTERED_USER (user_pk, user_name, password, email) values (DEFAULT, 'Ecoste', 'password', 'mail@mail.com')")
    except sqlalchemy.exc.IntegrityError:  # User already exists
        pass

    result = conn.execute("select user_pk from REGISTERED_USER")
    for row in result:
        user_pk = row['user_pk']

    s = text("insert into PRICE_POINT_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction) values (DEFAULT, :user_pk, FALSE, FALSE, '*', '*', 0.5, 'up')")
    conn.execute(s, user_pk=user_pk)
