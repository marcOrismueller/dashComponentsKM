import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from app import app, engine
import locale
from apps.fnc_container import helpers
import ast
from flask_login import current_user
from preprocessing import Preprocessing

# Windows:
#locale.setlocale(locale.LC_ALL, 'deu_deu')
# Ubuntu (Deployement Version):
#locale.setlocale(locale.LC_ALL, 'deu_deu.UTF-8')


# input_data = [
#     '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
#     '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
#     '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
#     '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
#     '3. Gang 1x Burger Royal 21.00 # Bratkartoffel # extra Champignon + 1.50 1x Filet Steak 50.20 # 180 g 37,90 # Medium Rare (50øC) # Bratkartoffeln +4,90 # Kartoffelgratin +4,90 # Pepper Jus +2,50 1x Filet Steak 68.20 # 300 g 57,90 Medium Well (60øC) # Pommes +4,90 # Knoblauchbrot +2,90 # Sauce Bearnaise +2,50',
# ]

# cards_headers = [
#     '16-Mar-21 13:15 1 Burgermeister',
#     '17-Mar-21 14:12 Burgermeister 2',
#     '18-Mar-21 13:15 Hypersoft 3 5',
#     '18-Mar-21 13:15 Burgermeister 2',
#     '19-Mar-21 13:15 Hypersoft 5 1',
# ]
# call Class & print results
p = Preprocessing([
        '1 08-Mar-20 15:40 Hypersoft Technik 100',
        '3 09-Mar-20 11:39 Hypersoft Technik 100',
        '5 26-Mar-21 14:01 1 Burgermeister', '8 01-Apr-21 09:03 1 Burgermeister 8',
        'KALTE KÜCHE 06-Apr-21 08:46 Hypersoft 1',
        'KALTE KÜCHE 06-Apr-21 08:51 Hypersoft 88',
        'WARM / GRILL 06-Apr-21 08:51 Hypersoft 88',
        'KALTE KÜCHE 15-Apr-21 15:51 Hypersoft 12',
        'Kitchendisplay 2919. 15-Apr-21 15:51 Hypersoft 12',
        'KALTE KÜCHE 15-Apr-21 15:55 Hypersoft 12',
        'Kitchendisplay 2935. 15-Apr-21 15:55 Hypersoft 12',
        'WARM / GRILL 15-Apr-21 15:55 Hypersoft 12',
        'DESSERT 15-Apr-21 15:55 Hypersoft 12',
        'PIZZA&PASTA 15-Apr-21 15:55 5 Restaurant Hypersoft 12',
        'PIZZA&PASTA 15-Apr-21 15:56 5 Restaurant Hypersoft 12',
        'KALTE KÜCHE 21-Apr-21 10:14 Hypersoft 2',
        'PIZZA&PASTA 21-Apr-21 10:14 5 Restaurant Hypersoft 2'
    ], [
        '1x Pink Persia Poutine + auf Knoblauchfritten', 
        '1x Tijuana Street Fries + auf Knoblauchfritten', 
        '2x Afri Cola 0,2l', 
        'INHOUSE 1x Bluna Orange 0,2l 1x Bluna Zitrone 0,2l', 
        '1x Salat California 8.50/ 1 #Standard 8.50/ 1 # French Dressing ', 
        '2. Gang 1x Hirschplttli 1 Pers. 12.00/ 9 #Standard Pers. 12.00/ 9 1x Roastbeef 8.00/ 9 8.00/ 9 #Standard 8.00/ 9 1x Salat California 8.50/ 8 #Standard 8.50/ 8 # American Dressing ', 
        'WARM / GRILL 06-Apr-21 08:51 Hypersoft 88 1x Filet Steak 0.00/ 0 #Standard 0.00/ 0 1x Filet Steak 50.20/ 0 #Standard 50.20/ 0 # 180 g 37,90 # Rare/Blutig 40øC 2x Pommes +4,90 # BBQ Sauce +2,50. Gang 2,50,50 1x Filet Steak 70.20/ 0 #Standard 70.20/ 0 # 300 g 57,90 # Medium Well 60øC # gem. Salat +4,90 # Wok-Gemüse +4,90 # BBQ Sauce +2,50 ', 
        '1. Gang 1x Club Sandwich 8.50/ 3 #Standard 8.50/ 3 1x Salat California 8.50/ 1 #Standard 8.50/ 1 # American Dressing ', 
        'Kitchendisplay 2919. 15-Apr-21 15:51 Hypersoft 12 1. Gang 1x Lachssalat 6.50 #Standard 6.50 ', 
        '3. Gang 1x Rotes Curry mit Hhnchen 12.00/ 3 #Standard hnchen 12.00/ 3 4. Gang hnchen 12.00/ 3 hnchen 12.00/ 3 1x Mousse au Chocolate 8.00/ 3 #Standard te 8.00/ 3 1x Tiramisu 8.00/ 2 #Standard 8.00/ 2 ', 
        'Kitchendisplay 2935. 15-Apr-21 15:55 Hypersoft 12 2. Gang 1x Pizza Prosciutto Crudo 13.50 #Standard Crudo 13.50 ', 
        '3. Gang 1x Filet Steak 50.20/ 1 #Standard 50.20/ 1 # 180 g 37,90 # Medium 55øC # Bratkartoffeln +4,90 # Kartoffelgratin +4,90 # Pepper Jus +2,50 1x Filet Steak 68.20/ 2 #Standard 68.20/ 2 # 300 g 57,90 # Medium Well 60øC # Knoblauchbrot +2,90 # Maiskolben +4,90 # Sauce Bearnaise +2,50 ', 
        'DESSERT 15-Apr-21 15:55 Hypersoft 12 4. Gang 1x Albisbecher 12.00 #Standard 12.00 ', 
        'PIZZA&PASTA 15-Apr-21 15:55 5 Restaurant Hypersoft 12 2. Gang 1x Pizza Burrata 17.50 #Standard 17.50', 
        'PIZZA&PASTA 15-Apr-21 15:56 5 Restaurant Hypersoft 12 2. Gang 1x Pizza Arrapato 15.50 #Standard 15.50', 
        '1. Gang 1x Ribollita 6.50/ 1 #Standard 6.50/ 1 1x Tomatencremesuppe 6.50/ 2 #Standard 6.50/ 2 2. Gang 6.50/ 2 6.50/ 2 1x Chili con Carne 8.50/ 2 #Standard 8.50/ 2 ', 
        '2. Gang 1x Pizza Burrata 17.50/ 1 #Standard 17.50/ 1'
])


input_data = p.card_body()
cards_headers = p.card_header() 

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
            new_cards_values = helpers.food_cards_listings(listgroup_values, cards_headers)
            new_listgroup_values = helpers.foods_listing(new_cards_values)
            # new_listgroup_values = helpers.process_input_listgroup_v2(
            #     listgroup_values)
            # new_cards_values = helpers.process_input_cards_v2(
            #     cards_values, cards_headers)
            return {
                'initial': {
                    'listgroup_values': new_listgroup_values.to_dict('records'), 'cards_values': new_cards_values.to_dict('records')
                },
            }, ''
        else:
            return None, [dbc.Col(dbc.Alert("This is a danger alert. Scary!", color="danger"), width={"size": 6, "offset": 3})]
    return {}, ''
