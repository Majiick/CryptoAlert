from flask import Flask, render_template, current_app, redirect, url_for, request
import zmq
import pandas as pd
from influxdb import DataFrameClient
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user
from typing import List, Dict, Type
import uuid

app = Flask(__name__, static_folder='./static', template_folder='./static')
app.secret_key = b'8ae5144d0676496af705b6b3af000275f81ff1579a6eca72'
login_manager = LoginManager(app=app)


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __eq__(self, other):
        '''
        Checks the equality of two `UserMixin` objects using `get_id`.
        '''
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `UserMixin` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


logged_in_users: Dict[str, User] = dict()  # id to User
@login_manager.user_loader
def load_user(user_id):
    if user_id in logged_in_users:
        print('User logged in', flush=True)
        return logged_in_users[user_id]
    else:
        print('User not logged in', flush=True)
        return None


@app.route('/')
def index():
    return render_template('dist/index.html')


@app.route('/login', methods=['POST'])
def login():
    print(request.data)

    user = User(uuid.uuid4().hex)
    logged_in_users[user.get_id()] = user
    login_user(user)
    print('New user logged in', flush=True)

    return redirect(url_for('index'))


@app.route('/logintest')
def logged_in_test():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    return 'Logged in, your used id is: ' + current_user.get_id()


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
