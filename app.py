import dash
import dash_bootstrap_components as dbc
import warnings
import datetime
from sqlalchemy import Table, create_engine, ForeignKey, DateTime
from flask_sqlalchemy import SQLAlchemy
import configparser
import os
from flask_login import logout_user, LoginManager, UserMixin

warnings.filterwarnings("ignore")

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css', 
    ]

engine = create_engine('mysql://root:@localhost/marcdb')
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
    company_company_id = db.Column(db.Integer, ForeignKey('company.company_id'))

User_tbl = Table('users', User.metadata)

app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, external_stylesheets, dbc.themes.GRID], 
    title='SaCoSo KM',
    update_title=None,
)

#app.config['suppress_callback_exceptions'] = True

server = app.server
app.config.suppress_callback_exceptions = True
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI='mysql://root:@localhost/marcdb',
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
