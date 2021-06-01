from dash.exceptions import PreventUpdate
from dash_core_components.Location import Location
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from app import app, User
from werkzeug.security import check_password_hash
from flask_login import login_user

layout = html.Div(children=[
    dcc.Location(id='url_login', refresh=True),
    html.Div([
        html.Form([
            html.Div([
                html.Div([
                    html.H2('Login'),
                    html.Div([
                        dcc.Input(placeholder='Email', type='email', id='uemail_box')
                    ], className='form-row'),
                    html.Div([
                        dcc.Input(placeholder='Password', type='password', id='pwd_box')
                    ], className='form-row'),
                ]),
                html.Div(children='', id='output-state', className='form-row'),
                html.Div([
                    dbc.Button('Login', className='submit', id='login_btn', n_clicks=0),
                    html.A('Sign up', className='link', href='/signup')
                ], className='form-row-last')
            ], className='form-left')
        ], className='form-detail')
    ], className='form-v10-content', style={'maxWidth': '600px'})
], className='page-content')

@app.callback(
    Output('url_login', 'pathname'), 
    Input('login_btn', 'n_clicks'),
    State('uemail_box', 'value'), 
    State('pwd_box', 'value')
)
def successful(n_clicks, input1, input2):
    if n_clicks > 0:
        user = User.query.filter_by(user_email=input1.strip()).first()
        if user:
            if check_password_hash(user.user_password, input2):
                login_user(user)
                return '/items-selection'
            else:
                pass
        else:
            pass
    else: 
        raise PreventUpdate

@app.callback(
    Output('output-state', 'children')
    , [Input('login_btn', 'n_clicks')]
    , [State('uemail_box', 'value'), State('pwd_box', 'value')])
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = User.query.filter_by(user_email=input1.strip()).first()
        if user:
            if check_password_hash(user.user_password, input2):
                return ''
            else:
                return html.B('Incorrect email or password', style={'color': 'red'})
        else:
            return html.B('Incorrect email or password', style={'color': 'red'})
    else: 
        raise PreventUpdate