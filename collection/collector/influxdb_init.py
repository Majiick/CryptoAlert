from influxdb import InfluxDBClient
import requests
import time
from mlogging import logger

def create_client():
    host = 'influxdb'
    port = 8086
    user = 'root'
    password = 'root'
    dbname = 'financial'

    try:
        client = InfluxDBClient(host, port, user, password, dbname)
    except Exception as e:
        # Wait for the DB to startup.
        time.sleep(10)
        client = InfluxDBClient(host, port, user, password, dbname)
    return client

db_client = create_client()
try:
    db_client.create_database('financial')
except Exception as e:
    # Wait for the DB to startup.
    time.sleep(10)
    db_client.create_database('financial')

