import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_dangerously_set_inner_html
from werkzeug.security import generate_password_hash
import sqlite3
from app import app, engine
from datetime import datetime

layout = html.Div(id='registration', children=[
    html.Div(id='create_user_output'),
    dcc.Location(id='create_user', refresh=True),
    html.Div([
        html.Form([
            html.Div([
                html.H2('User Infomation'),
                html.Div([
                    html.Div([
                        dcc.Input(placeholder='First Name', id='ufname_box'),
                    ], className='form-row form-row-1'),
                    html.Div([
                        dcc.Input(placeholder='Last Name', id='ulname_box'),
                    ], className='form-row form-row-2')
                ], className='form-group'),
                html.Div([
                    dcc.Input(placeholder='Email',
                              type='email', id='uemail_box')
                ], className='form-row'),
                html.Div([
                    html.Div([
                        dcc.Input(placeholder='Code +',
                                  type='text', className='code', id='ucode_box')
                    ], className='form-row form-row-1'),
                    html.Div([
                        dcc.Input(placeholder='Phone Number',
                                  type='text', id='uphone_box')
                    ], className='form-row form-row-2')
                ], className='form-group'),
                html.Div([
                    dcc.Input(placeholder='Password',
                              type='password', id='upwd_box1'),
                ], className='form-row'),
                html.Div([
                    dcc.Input(placeholder='Repeat password',
                              type='password', id='upwd_box2'),
                ], className='form-row')

            ], className='form-left'),
            html.Div([
                html.Div([
                    html.H2('Company Information'),
                    html.Div([
                        dcc.Input(placeholder='Company Name',
                                  type='text', id='company_name')
                    ], className='form-row'),
                    html.Div([
                        dcc.Input(placeholder='CEO Name',
                                  type='text', id='company_ceo')
                    ], className='form-row'),
                ], className='signup_disabled'),
                html.Div([
                    html.H2('Restaurant Details'),
                    html.Div([
                        dcc.Input(placeholder='Restaurant Name',
                                  type='text', id='restaurant_name')
                    ], className='form-row'),
                    html.Div([
                        dcc.Input(placeholder='Street + Nr',
                                  type='text', className='street', id='restaurant_steet')
                    ], className='form-row'),
                    html.Div([
                        dcc.Input(placeholder='Additional Information',
                                  type='text', className='additional', id='restaurant_additional')
                    ], className='form-row'),
                    html.Div([
                        html.Div([
                            dcc.Input(placeholder='Zip Code',
                                      type='text', className='zip', id='restaurant_zipcode')
                        ], className='form-row form-row-1'),
                        html.Div([
                            html.Select([
                                html.Option('Place', value='Place'),
                                html.Option('Street', value='Street'),
                                html.Option('District', value='District'),
                                html.Option('City', value='City'),
                            ], name='Place', id='place'),
                            html.Span([
                                dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                                        <i class="fa fa-sort-desc fa-2x"></i>
                                    '''),
                            ], className='select-btn')
                        ], className='form-row form-row-2')
                    ], className='form-group'),
                    html.Div([
                        html.Select([
                            html.Option('Germany')
                        ], id='country')
                    ], className='form-row'),
                ], className='signup_disabled', style={'marginTop': '30px'}),
                html.Div([

                ], className='form-checkbox'),
                html.Div([
                    dbc.Button('Register', className='submit',
                               id='register_btn', n_clicks=0),
                ], className='form-row-last'),
                html.Div([
                    dbc.Toast(
                        "Please make sure you have entered all the required information!!",
                        id="error_input_popup",
                        header="Invalid Informations",
                        is_open=False,
                        dismissable=True,
                        icon="danger",
                        # top: 66 positions the toast below the navbar
                        style={"position": "fixed", "top": 66,
                               "right": 10, "width": 350},
                        className='toast'
                    ),
                    dbc.Toast(
                        "Your account has been successfully registered. Please Log in to your account",
                        id="success_input_popup",
                        header="Success ",
                        is_open=False,
                        dismissable=True,
                        icon="success",
                        # top: 66 positions the toast below the navbar
                        style={"position": "fixed", "top": 66,
                               "right": 10, "width": 350},
                        className='toast'
                    ),
                ])
            ], className='form-right')
        ], className='form-detail')
    ], className='form-v10-content')
], className='page-content')


@app.callback(
    Output('create_user', "location"),
    Output("error_input_popup", "is_open"),
    Output('success_input_popup', 'is_open'),
    Input('register_btn', 'n_clicks'),
    State('ufname_box', 'value'),
    State('ulname_box', 'value'),
    State('uemail_box', 'value'),
    State('ucode_box', 'value'),
    State('uphone_box', 'value'),
    State('upwd_box1', 'value'),
    State('upwd_box2', 'value'),
    # State('company_name', 'value'),
    # State('company_ceo', 'value'),
    # State('restaurant_name', 'value'),
    # State('restaurant_steet', 'value'),
    # State('restaurant_additional', 'value'),
    # State('restaurant_zipcode', 'value'),
    # State('place', 'value'),
    # State('country', 'value')
)
def insert_users(
    n_clicks,
    ufname_box,
    ulname_box,
    uemail_box,
    ucode_box,
    uphone_box,
    upwd_box1,
    upwd_box2,
    # company_name,
    # company_ceo,
    # restaurant_name,
    # restaurant_steet,
    # restaurant_additional,
    # restaurant_zipcode,
    # place,
    # country
):
    params = [
        ufname_box,
        ulname_box,
        uemail_box,
        ucode_box,
        uphone_box,
        upwd_box1,
        upwd_box2,
        # company_name,
        # company_ceo,
        # restaurant_name,
        # restaurant_steet,
        # restaurant_additional,
        # restaurant_zipcode,
        # 'city',
        # 'germany'
    ]
    if not n_clicks:
        raise PreventUpdate

    if len([x for x in params if x]) == len(params):
        if upwd_box1 == upwd_box2:
            hashed_password = generate_password_hash(
                upwd_box1, method='sha256')
            # connection = sqlite3.connect('app.db')
            # connection.row_factory = sqlite3.Row
            # conn = connection.cursor()
            conn = engine.connect()
            conn.execute(f"""
                INSERT INTO user 
                    (
                        user_fname, 
                        user_lname, 
                        user_email,
                        user_phone,
                        user_password
                    ) 
                VALUES (
                    '{ufname_box}',
                    '{ulname_box}',
                    '{uemail_box}', 
                    '{ucode_box} {uphone_box}',
                    '{hashed_password}'
                );
            """)
            conn.close()
            return '/login', False, True

            # #connection.commit()
            # conn.execute(f"""
            #     INSERT INTO restaurant
            #         (
            #             restaurant_name,
            #             restaurant_addr_street,
            #             restaurant_addr_zip_code,
            #             restaurant_addr_zip_type,
            #             restaurant_addr_country,
            #             restaurant_created,
            #             restaurant_modified,
            #             user_id
            #         )
            #     VALUES (
            #         '{restaurant_name}',
            #         '{restaurant_steet}',
            #         '{restaurant_zipcode}',
            #         'city',
            #         'germany',
            #         '{datetime.today()}',
            #         '{datetime.today()}',
            #         (
            #             SELECT id
            #             FROM user
            #             WHERE user_email = "{uemail_box}"
            #         )
            #     );
            # """)

            # conn.close()

            # conn.execute(f"""
            #     INSERT INTO company (company_name, company_ceo_name, user_id)
            #     VALUES (
            #         '{company_name}',
            #         '{company_ceo}',
            #         (
            #             SELECT id
            #             FROM user
            #             WHERE user_email = '{uemail_box}'
            #         )
            #         );

            # """)

    else:
        return '/signup', True, False
