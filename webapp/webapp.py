from flask import Flask, render_template
import zmq
import pandas as pd
from influxdb import DataFrameClient
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dbtest')
def db_test():
    host = 'influxdb'
    port = 8086
    user = 'root'
    password = 'root'
    dbname = 'demo'
    # Temporarily avoid line protocol time conversion issues #412, #426, #431.
    protocol = 'json'
    client = DataFrameClient(host, port, user, password, dbname)
    print("Create pandas DataFrame")
    df = pd.DataFrame(data=list(range(30)),
                      index=pd.date_range(start='2014-11-16',
                                          periods=30, freq='H'))

    print("Create database: " + dbname)
    client.create_database(dbname)

    print("Write DataFrame")
    client.write_points(df, 'demo')

    print("Write DataFrame with Tags")
    client.write_points(df, 'demo',
                        {'k1': 'v1', 'k2': 'v2'})

    print("Read DataFrame")
    client.query("select * from demo")

    # print("Delete database: " + dbname)
    # client.drop_database(dbname)
    return 'WTF'
