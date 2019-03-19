from flask import Flask, render_template, current_app, redirect, url_for, request, jsonify
import zmq
import pandas as pd
from influxdb import DataFrameClient
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user
from typing import List, Dict, Type
from postgres_init import engine
import uuid
from sqlalchemy.sql import text
from flask_jwt import JWT, jwt_required, current_identity



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


def authenticate_jwt(user_name, password):
    with engine.begin() as conn:
        result = conn.execute(text("select user_pk from REGISTERED_USER WHERE LOWER(user_name) = LOWER(:user_name) AND password = :password"), user_name = user_name, password = password)
        row = result.fetchone()

        if row:
            user = User(row['user_pk'])
            return user
        else:
            return None

def identity_jwt(payload):
    user_pk = payload['identity']

    with engine.begin() as conn:
        result = conn.execute(text("select user_pk from REGISTERED_USER WHERE user_pk = :user_pk"), user_pk = user_pk)
        row = result.fetchone()

        if row:
            user = User(row['user_pk'])
            return user
        else:
            return None


########################################################################################################################################################
logged_in_users: Dict[str, User] = dict()  # id to User
app = Flask(__name__, static_folder='./static', template_folder='./static')
app.secret_key = b'8ae5144d0676496af705b6b3af000275f81ff1579a6eca72'
login_manager = LoginManager(app=app)
jwt = JWT(app, authenticate_jwt, identity_jwt)
########################################################################################################################################################


@login_manager.user_loader
def load_user(user_id):
    if user_id in logged_in_users:
        print('User is logged in', flush=True)
        return logged_in_users[user_id]
    else:
        print('User is not logged in', flush=True)
        return None


@app.route('/')
def index():
    return render_template('dist/index.html')


@app.route('/login', methods=['POST'])
def login():
    user_name = request.json['username']
    password = request.json['password']

    with engine.begin() as conn:
        result = conn.execute(text("select user_pk from REGISTERED_USER WHERE LOWER(user_name) = LOWER(:user_name) AND password = :password"), user_name = user_name, password = password)
        row = result.fetchone()

        if row:
            user = User(row['user_pk'])
            logged_in_users[user.get_id()] = user
            login_user(user)
            print('New user logged in', flush=True)
            return 'Logged in successfully'
        else:
            return 'invalid login'
    
    return 'invalid login'


@app.route('/register', methods=['POST'])
def register():
    pass


@app.route('/logintest')
def logged_in_test():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    return 'Logged in, your used id is: ' + current_user.get_id()


@app.route('/getsubscribedalerts')
@jwt_required()
def get_subscribed_alerts():
    # All lower case
    ret = {}  # ret{<table_name> : [list of table json objects]} e.g. ret['price_point_alert'] = [{alert_pk: 1, created_by_user: 2, etc...}]

    with engine.begin() as conn:
        ret['price_point_alert'] = []
        result = conn.execute(text("SELECT exchange, pair, point, direction FROM PRICE_POINT_ALERT WHERE created_by_user = :user_pk"),
                              user_pk=current_identity.get_id())  # current_identity is JWT's proxy for User class

        for row in result:
            d = dict(row.items())
            ret['price_point_alert'].append(d)

    return jsonify(ret)


@app.route('/createalert', methods=['POST'])
@jwt_required()
def create_alert():
    # JSON Data example: {'alert': 'pricepoint', 'pair': ['btceth'], 'exchange': ['kraken', 'poloniex'], 'point': '3432', 'below_above': 'below'}
    # TODO: Verify the data.
    if len(request.json['pair']) > 1 or len(request.json['exchange']) > 1:
        return jsonify({'success': False, 'error': 'More than one pair or exchange is not supported yet.'})

    dir = ''
    if request.json['below_above'] == 'below':
        dir = 'down'
    elif request.json['below_above'] == 'above':
        dir = 'up'
    else:
        return jsonify({'success': False, 'error': 'Need to specify below or above'})

    print(request.json, flush=True)
    with engine.begin() as conn:
        s = text('insert into PRICE_POINT_ALERT (alert_pk, created_by_user, fulfilled, repeat, exchange, pair, point, direction, alert_type) values (DEFAULT, :user_pk, FALSE, FALSE, :exchange, :pair, :point, :direction, "pricepoint") RETURNING alert_pk')
        cursor = conn.execute(s, user_pk=current_identity.get_id(), exchange=request.json['exchange'][0], pair=request.json['pair'][0], point=float(request.json['point']), direction=dir)
        created_alert_pk = cursor.fetchone()[0]

        # TEMPORARY TEMPORARY
        #################################################################################################################
        s = text("INSERT INTO EMAIL_NOTIFICATION (notification_pk, notify_on_which_alert, user_to_notify) VALUES (DEFAULT, :alert_pk, :user_pk)")
        conn.execute(s, alert_pk=created_alert_pk, user_pk=current_identity.get_id())

    return jsonify({'success': True})


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
