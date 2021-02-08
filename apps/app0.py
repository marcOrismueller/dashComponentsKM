import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State, ALL
import json
import dash
from dash.exceptions import PreventUpdate

from app import app


list_1 = ['5 Red', '3 Green 6 Yellow', '3 Blue', '8 Red', '9 Indigo', '18 DarkRed', '12 DarkKhaki', '5 Pink', '2 Red']
list_2 = ['10 Red 7 Yellow', '8 Blue', '4 Green', '5 Pink 10 Indigo', '20 DarkRed', '12 DarkKhaki', '1 Red']


layout = html.Div(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3", 
                    placeholder="List_2 (ListGroup elements)", 
                    id='listgroup_values', 
                    value='5 Red, 3 Green 6 Yellow, 3 Blue, 8 Red, 9 Indigo, 18 DarkRed, 12 DarkKhaki, 5 Pink, 2 Red'   
                ) 
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3", 
                    placeholder="List_1 (Cards elements)", 
                    id='cards_values', 
                    value='10 Red 7 Yellow, 8 Blue, 4 Green, 5 Pink 10 Indigo, 20 DarkRed, 12 DarkKhaki, 1 Red'
                ),
            ], width={"size": 6, "offset": 3})
        ], style={'alignItems': 'center'}),
        dbc.Row(id='upload_alert'),
        dbc.Row([
            dbc.Col([
                dcc.Link(
                    dbc.Button("Load", outline=True, color="dark", id='load_btn', block=True),
                    href='/'
                ),
            ], width={"size": 3, "offset": 6})
        ])
    ]), style={'marginTop': '100px'}
)



@app.callback(
    Output('input_data', 'data'),
    Output('upload_alert', 'children'),
    Input('load_btn', 'n_clicks'),
    State('listgroup_values', 'value'),
    State('cards_values', 'value'),
)
def upload_data(n_clicks, listgroup_values, cards_values):
    if n_clicks:
        listgroup_values = [item.strip() for item in listgroup_values.split(',')]
        cards_values = [item.strip() for item in cards_values.split(',')]
        if listgroup_values and cards_values:
            return {
                'initial':{
                    'listgroup_values': listgroup_values, 'cards_values': cards_values
                }}, ''
        else: 
            return None, [dbc.Col(dbc.Alert("This is a danger alert. Scary!", color="danger"), width={"size": 6, "offset": 3})]
    return {}, ''