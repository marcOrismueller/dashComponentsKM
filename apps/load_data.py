import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from app import app
import locale
from apps.fnc_container import helpers
import ast


# Windows:
#locale.setlocale(locale.LC_ALL, 'deu_deu')
# Ubuntu (Deployement Version):
#locale.setlocale(locale.LC_ALL, 'deu_deu.UTF-8')

# input_data = ['1 Pink Persia Poutine + auf Knoblauchfritten ', '1 Portion Hausfritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Tijuana Street Fries + auf Hausfritten ', '2 Portion Knoblauchfritten 3 Portion Se Fritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Currywurst Frittenwerk Spezial + auf Knoblauchfritten ', '1 Tijuana Street Fries + auf Knoblauchfritten ',
#               '1 Pink Persia Poutine + auf Knoblauchfritten ', '1 Portion Hausfritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Tijuana Street Fries + auf Hausfritten ', '2 Portion Knoblauchfritten 3 Portion Se Fritten ', '1 Classic Quebec Poutine + auf Hausfritten 1 Currywurst Frittenwerk Spezial + auf Knoblauchfritten ', '1 Tijuana Street Fries + auf Knoblauchfritten ']
# cards_headers = ['08-Dez-20 15:40 Hypersoft Technik 1 100', '08-Dez-20 15:40 Hypersoft Technik 2 102', '10-Dez-20 16:19 Hypersoft Technik 102', '10-Dez-20 11:36 Hypersoft Technik 3 100', '10-Dez-20 11:38 Hypersoft Technik 4 101', '11-Dez-20 11:39 Hypersoft Technik 5 104', '08-Dez-20 15:40 Hypersoft Technik 5 100', '13-Dez-20 15:40 Hypersoft Technik 4 108', '11-Dez-20 16:19 Hypersoft Technik 2 100',
#                  '15-Dez-20 11:36 Hypersoft Technik 2 106', '09-Dez-20 11:38 Hypersoft Technik 3 106', '15-Dez-20 11:39 Hypersoft Technik 2 100']


input_data = [
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '3. Gang 1x Burger Royal 21.00 # Bratkartoffel # extra Champignon + 1.50 1x Filet Steak 50.20 # 180 g 37,90 # Medium Rare (50øC) # Bratkartoffeln +4,90 # Kartoffelgratin +4,90 # Pepper Jus +2,50 1x Filet Steak 68.20 # 300 g 57,90 Medium Well (60øC) # Pommes +4,90 # Knoblauchbrot +2,90 # Sauce Bearnaise +2,50',
]

cards_headers = [
    '16-Mar-21 13:15 1 Burgermeister',
    '17-Mar-21 14:12 Burgermeister 2',
    '18-Mar-21 13:15 Hypersoft 3 5',
    '18-Mar-21 13:15 Burgermeister 2',
    '19-Mar-21 13:15 Hypersoft 5 1',
]


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
        listgroup_values = ast.literal_eval(listgroup_values)
        cards_values = ast.literal_eval(cards_values)
        cards_headers = ast.literal_eval(cards_headers)

        if listgroup_values and cards_values and cards_headers:
            new_listgroup_values = helpers.process_input_listgroup_v2(
                listgroup_values)
            new_cards_values = helpers.process_input_cards_v2(
                cards_values, cards_headers)
            return {
                'initial': {
                    'listgroup_values': new_listgroup_values.to_dict('records'), 'cards_values': new_cards_values.to_dict('records')
                },
            }, ''
        else:
            return None, [dbc.Col(dbc.Alert("This is a danger alert. Scary!", color="danger"), width={"size": 6, "offset": 3})]
    return {}, ''
