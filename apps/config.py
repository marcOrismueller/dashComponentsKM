import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from app import app, engine
import locale
from apps.fnc_container import helpers, crud_op_db, read_files
import ast
from flask_login import current_user
from preprocessing import Preprocessing
import os.path
from os import path

layout = html.Div(
    dbc.Container([
        dbc.Toast(
            "The folder path is saved successfully!..",
            id="success_path",
            header="Files path",
            is_open=False,
            #dismissable=True,
            duration=2000,
            icon="success",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 66,
                    "right": 10, "width": 350},
            className='toast'
        ),
        dbc.Row([
            dbc.Col([
                html.P('Insert the folder path:'),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Input(placeholder="........./printers/", type="text", id='folder_path'),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Link(
                    dbc.Button("Save", outline=True, color="dark",
                               id='save_path', block=True),
                    href=''
                ),
            ], width={"size": 3, "offset": 6})
        ])
    ]), style={'marginTop': '100px'}
)


@app.callback(
    Output('success_path', 'children'),
    Output('success_path', 'icon'),
    Output('success_path', 'is_open'),
    Input('save_path', 'n_clicks'),
    State('folder_path', 'value')
)
def get_printer_folder_path(n_clicks, folder_path):
    if not n_clicks:
        raise PreventUpdate

    if n_clicks:
        if path.exists(folder_path):
            r = crud_op_db.update_printers_folder_path(folder_path)
            #read_files.update_data()
            return 'Path saved successfully', 'success', True
        else:
            return  'Path is not valid!', 'danger', False
    raise PreventUpdate
