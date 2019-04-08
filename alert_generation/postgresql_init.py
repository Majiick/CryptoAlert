import sqlalchemy
import psycopg2
import time
from sqlalchemy.sql import text
from mlogging import logger

file = open('postgresql_init.sql')
engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:password@postgres')
escaped_sql = sqlalchemy.text(file.read())

try:
    engine.execute(escaped_sql)
except sqlalchemy.exc.OperationalError:
    time.sleep(10)  # Wait for postgres to startup.
    engine.execute(escaped_sql)

with engine.begin() as conn:
    ### TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY TEMPORARY
    ############################################################################################################################
    try:
        conn.execute("insert into REGISTERED_USER (user_pk, user_name, password, email) values (DEFAULT, 'Ecoste', crypt('password', gen_salt('md5')), 'ecostequse@gmail.com')")
    except sqlalchemy.exc.IntegrityError:  # User already exists
        pass
    ############################################################################################################################

    result = conn.execute("select user_pk from REGISTERED_USER")
    for row in result:
        user_pk = row['user_pk']

    # s = text("insert into PRICE_POINT_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction) values (DEFAULT, :user_pk, FALSE, FALSE, '*', '*', 0.5, 'up')")
    # conn.execute(s, user_pk=user_pk)
    #
    # s = text("insert into VOLUME_POINT_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point) values (DEFAULT, :user_pk, FALSE, FALSE, '*', '*', 1)")
    # conn.execute(s, user_pk=user_pk)

    s = text("insert into PRICE_PERCENTAGE_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, time_frame, broadcast_interesting_event_on_trigger, alert_type) values (DEFAULT, :user_pk, FALSE, TRUE, '*', '*', 0.01, 'up', 60, TRUE, 'pricepercentage')")
    conn.execute(s, user_pk=user_pk)
    s = text("insert into PRICE_PERCENTAGE_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, time_frame, broadcast_interesting_event_on_trigger, alert_type) values (DEFAULT, :user_pk, FALSE, TRUE, '*', '*', 0.01, 'down', 60, TRUE, 'pricepercentage')")
    conn.execute(s, user_pk=user_pk)
    s = text("insert into PRICE_PERCENTAGE_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, time_frame, broadcast_interesting_event_on_trigger, alert_type) values (DEFAULT, :user_pk, FALSE, TRUE, '*', '*', 1, 'down', 300, TRUE, 'pricepercentage')")
    conn.execute(s, user_pk=user_pk)
    s = text("insert into PRICE_PERCENTAGE_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, time_frame, broadcast_interesting_event_on_trigger, alert_type) values (DEFAULT, :user_pk, FALSE, TRUE, '*', '*', 1, 'up', 300, TRUE, 'pricepercentage')")
    conn.execute(s, user_pk=user_pk)
    s = text("insert into PRICE_PERCENTAGE_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, time_frame, broadcast_interesting_event_on_trigger, alert_type) values (DEFAULT, :user_pk, FALSE, TRUE, '*', '*', 2.5, 'up', 60, TRUE, 'pricepercentage')")
    conn.execute(s, user_pk=user_pk)
    s = text("insert into PRICE_PERCENTAGE_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, time_frame, broadcast_interesting_event_on_trigger, alert_type) values (DEFAULT, :user_pk, FALSE, TRUE, '*', '*', 5, 'up', 300, TRUE, 'pricepercentage')")
    conn.execute(s, user_pk=user_pk)


    s = text("insert into INTERESTING_EVENT (event_time, exchange, market, message, event_type) values (-5, 'testing xchange', 'test_test', 'test msg', 'test event')")
    conn.execute(s)


    """CREATE TABLE IF NOT EXISTS INTERRUPTION(
      id SERIAL PRIMARY KEY,
      start_time BIGINT NOT NULL,
      end_time BIGINT NOT NULL,
      exchange TEXT NOT NULL,
      fulfilled BOOLEAN NOT NULL,
      times_tried INTEGER
    );"""
    s = text("insert into INTERRUPTION (id, start_time, end_time, exchange, fulfilled, times_tried) VALUES (DEFAULT, 1554684573, 1554684773, 'BITTREX', FALSE, 0)")
    conn.execute(s)
