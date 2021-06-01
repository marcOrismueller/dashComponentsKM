import dash
import dash_bootstrap_components as dbc
import warnings
import datetime
from sqlalchemy import Table, create_engine, DateTime
from flask_sqlalchemy import SQLAlchemy
import configparser
import os
from flask_login import LoginManager, UserMixin
import configs

warnings.filterwarnings("ignore")

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css', 
    ]

credentials_db = f'mysql+mysqldb://{configs.username}:{configs.password}@{configs.host}:{configs.port}/{configs.database}'
engine = create_engine(credentials_db)
db = SQLAlchemy()
config = configparser.ConfigParser()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_fname = db.Column(db.String(45), nullable = False)
    user_lname = db.Column(db.String(45), nullable = False)
    user_email = db.Column(db.String(45), unique = True)
    user_phone = db.Column(db.String(45))
    user_password = db.Column(db.String(255))
    user_created = db.Column(DateTime, default=datetime.datetime.utcnow)
    user_modified = db.Column(DateTime, default=datetime.datetime.utcnow)

User_tbl = Table('users', User.metadata)

app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, external_stylesheets],  #, dbc.themes.GRID
    title='SaCoSo KM',
    update_title=None,
)

server = app.server
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI=credentials_db,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db.init_app(server)
# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'
#User as base
# Create User class with UserMixin
class User(UserMixin, User):
    pass