import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
import re
from dash.exceptions import PreventUpdate
import pandas as pd
from app import app


def process_input_listgroup(data_elements):
    quantity = {}
    cards_vals = {}
    for i, d in enumerate(data_elements):
        # split string after every number or '+' operation
        cards_vals[i] = []
        d = re.split(r'\s?(\d+|\+)\s?', d)
        # add up all elements separately
        for idx, value in enumerate(d):
            if value.isdigit() or value == '+':
                if value == '+':
                    count = 1
                else:
                    count = int(value)
                
                data = d[idx + 1]
                
                cards_vals[i].append({
                    f'{data}': count
                })
                
                quantity[data] = quantity.get(data, 0) + count
    
    df = pd.DataFrame()
    df['type'] = list(quantity.keys())
    df['quantity'] = list(quantity.values())
    df['type_id_str'] =  df['type'].str.lower().str.replace(' ', '_')
    df['type_id_int'] =  list(range(len(df['type'])))

    # If the select any cards selected field = 1
    return df


def process_input_cards(data_elements):
    cards_vals = pd.DataFrame()
    for i, d in enumerate(data_elements):
        # split string after every number or '+' operation
        d = re.split(r'\s?(\d+|\+)\s?', d)
        # add up all elements separately
        opt_id = 0
        for idx, value in enumerate(d):
            if value.isdigit() or value == '+':
                if value == '+':
                    count = 1
                else:
                    count = int(value)
                
                data = d[idx + 1]
                
                cards_vals = cards_vals.append({
                        'type': f'{value} {data}', 
                        'quantity': count,
                        'type_id_str': data.lower().strip().replace(' ', '_'), 
                        'type_id_int': int(i),
                        'opt_id': int(opt_id)
                    }, ignore_index=True)
                opt_id += 1

    # If the select any cards selected field = 1
    return cards_vals


layout = html.Div(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3",
                    placeholder="List_2 (ListGroup elements)",
                    id='listgroup_values',
                    value="""['1 Pink Persia Poutine + auf Knoblauchfritten', '1 Portion Hausfritten', '1 Classic Quebec Poutine + auf Hausfritten 1 Tijuana Street Fries + auf Hausfritten', '2 Portion Knoblauchfritten 3 Portion Se Fritten', '1 Classic Quebec Poutine + auf Hausfritten 1 Currywurst Frittenwerk Spezial + auf Knoblauchfritten', '1 Tijuana Street Fries + auf Knoblauchfritten']"""
                )
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3",
                    placeholder="List_1 (Cards elements)",
                    id='cards_values',
                    value="""['1 Pink Persia Poutine + auf Knoblauchfritten', '1 Portion Hausfritten', '1 Classic Quebec Poutine + auf Hausfritten 1 Tijuana Street Fries + auf Hausfritten', '2 Portion Knoblauchfritten 3 Portion Se Fritten', '1 Classic Quebec Poutine + auf Hausfritten 1 Currywurst Frittenwerk Spezial + auf Knoblauchfritten', '1 Tijuana Street Fries + auf Knoblauchfritten']"""
                ),
            ], width={"size": 6, "offset": 3})
        ], style={'alignItems': 'center'}),
        dbc.Row(id='upload_alert'),
        dbc.Row([
            dbc.Col([
                dcc.Link(
                    dbc.Button("Load", outline=True, color="dark",
                               id='load_btn', block=True),
                    href='/items-selection'
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
    if not n_clicks: 
        raise PreventUpdate

    if n_clicks:
        listgroup_values = [item.replace("'", '').strip() for item in listgroup_values.strip('][').split(',')]
        cards_values = [item.replace("'", '').strip() for item in cards_values.strip('][').split(',')]
        if listgroup_values and cards_values:
            new_listgroup_values = process_input_listgroup(listgroup_values)
            new_cards_values = process_input_cards(cards_values)
            return {
                'initial': {
                    'listgroup_values': new_listgroup_values.to_dict('records'), 'cards_values': new_cards_values.to_dict('records')
                },
            }, ''
        else:
            return None, [dbc.Col(dbc.Alert("This is a danger alert. Scary!", color="danger"), width={"size": 6, "offset": 3})]
    return {}, ''
