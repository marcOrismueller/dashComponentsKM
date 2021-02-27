import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from app import app
import locale
from apps.fnc_container import helpers

# Windows: 
#locale.setlocale(locale.LC_ALL, 'deu_deu')
# Ubuntu (Deployement Version): 
locale.setlocale(locale.LC_ALL, locale="German")

input_data = ['1 Pink Persia Poutine + auf Knoblauchfritten ', '1 Portion Hausfritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Tijuana Street Fries + auf Hausfritten ', '2 Portion Knoblauchfritten 3 Portion Se Fritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Currywurst Frittenwerk Spezial + auf Knoblauchfritten ', '1 Tijuana Street Fries + auf Knoblauchfritten ',
              '1 Pink Persia Poutine + auf Knoblauchfritten ', '1 Portion Hausfritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Tijuana Street Fries + auf Hausfritten ', '2 Portion Knoblauchfritten 3 Portion Se Fritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Currywurst Frittenwerk Spezial + auf Knoblauchfritten ', '1 Tijuana Street Fries + auf Knoblauchfritten ']
cards_headers = ['08-Dez-20 15:40 Hypersoft Technik 100', '08-Dez-20 15:40 Hypersoft Technik 100', '08-Dez-20 16:19 Hypersoft Technik 100', '09-Dez-20 11:36 Hypersoft Technik 100', '09-Dez-20 11:38 Hypersoft Technik 100', '09-Dez-20 11:39 Hypersoft Technik 100', '08-Dez-20 15:40 Hypersoft Technik 100', '08-Dez-20 15:40 Hypersoft Technik 100', '08-Dez-20 16:19 Hypersoft Technik 100',
                 '09-Dez-20 11:36 Hypersoft Technik 100', '09-Dez-20 11:38 Hypersoft Technik 100', '09-Dez-20 11:39 Hypersoft Technik 100']

layout = html.Div(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.P('List ELements'),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3",
                    placeholder="List_2 (ListGroup elements)",
                    id='listgroup_values',
                    value=str(input_data)
                )
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                html.P('Cards ELements'),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3",
                    placeholder="List_1 (Cards elements)",
                    id='cards_values',
                    value=str(input_data)
                ),
            ], width={"size": 6, "offset": 3})
        ], style={'alignItems': 'center'}),
        dbc.Row([
            dbc.Col([
                html.P('Cards Hearders'),
            ], width={"size": 6, "offset": 3})
        ], style={'marginBottom': '0px', 'paddingBottom': '0px'}),
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    className="mb-3",
                    placeholder="List_1 (Cards elements)",
                    id='cards_headers',
                    value=str(cards_headers)
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
    State('cards_headers', 'value')
)
def upload_data(n_clicks, listgroup_values, cards_values, cards_headers):
    if not n_clicks:
        raise PreventUpdate

    if n_clicks:
        listgroup_values = [item.replace("'", '').strip(
        ) for item in listgroup_values.strip('][').split(',')]
        cards_values = [item.replace("'", '').strip()
                        for item in cards_values.strip('][').split(',')]
        cards_headers = [item.replace("'", '').strip()
                         for item in cards_headers.strip('][').split(',')]
        if listgroup_values and cards_values and cards_headers:
            new_listgroup_values = helpers.process_input_listgroup(
                listgroup_values)
            new_cards_values = helpers.process_input_cards(
                cards_values, cards_headers)
            return {
                'initial': {
                    'listgroup_values': new_listgroup_values.to_dict('records'), 'cards_values': new_cards_values.to_dict('records')
                },
            }, ''
        else:
            return None, [dbc.Col(dbc.Alert("This is a danger alert. Scary!", color="danger"), width={"size": 6, "offset": 3})]
    return {}, ''
