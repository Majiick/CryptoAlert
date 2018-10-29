from influxdb import InfluxDBClient

def create_client():
    host = 'influxdb'
    port = 8086
    user = 'root'
    password = 'root'
    dbname = 'financial'
    return InfluxDBClient(host, port, user, password, dbname)

db_client = create_client()
db_client.create_database('financial')

