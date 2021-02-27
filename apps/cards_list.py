import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State, ALL
import json
import dash
from dash.exceptions import PreventUpdate
import json
from app import app
import pandas as pd
from apps.fnc_container import helpers as hlp
from datetime import datetime

def show_items(listgroup_values, mainCallBack=True):
    if mainCallBack:
        return [
            dbc.ListGroupItem(
                id={'id': 'lst_item', 'index': i},
                children=[f"{x['quantity']} {x['type']}"]
            )
            for i, x in listgroup_values.iterrows()
            if x['quantity'] > 0
        ]
    
    return dbc.ListGroup([
        dbc.ListGroupItem(
            id={'id': 'lst_item', 'index': x['type_id_int']},
            children=[f"{x['quantity']} {x['type']}"]
        )
        for i, x in listgroup_values.iterrows()
        if x['quantity'] > 0
    ], style={'marginTop': '10px', 'marginLeft': '10px'})


def show_cards(cards_values_df):
    def build_card_header(card_id): 
        card = cards_values_df.loc[cards_values_df['type_id_int'] == card_id]
        card_time = f'{card["card_time"].values[0]}'
        card_phrase = f'{card["card_phrase"].values[0]}'
        card_index = f'{card["card_index"].values[0]}'
        header = html.Div([
            html.P(card_index), 
            html.P(card_phrase), 
            html.P(card_time), 
        ], id='card_head')

        return header

    cards = html.Div([
        html.Div([
            dbc.Card(id={
                        'id': 'card',
                        'index': int(card_id)
                }, children=[
                dbc.CardHeader(build_card_header(card_id)),
                dbc.CardBody(
                    children=[
                        dbc.Checklist(
                            id={
                                'id': 'card_value',
                                'index': int(card_id)
                            },
                            options=hlp.create_checkbox_opt(cards_values_df.loc[cards_values_df['type_id_int'] == card_id]),
                            value=[], 
                            labelCheckedStyle={
                                "textDecoration": 'line-through',
                                },
                            className='hidden_box',
                            labelStyle={},
                        ),
                    ],
                    style={'textAlign': 'center', 'paddingRight': '60px'}
                ),

                dbc.CardFooter([
                    dbc.Button(
                        "Subtract",
                        outline=True,
                        color="success",
                        className="mr-1",
                        id={
                            'id': 'commit_substraction_btn',
                            'index': int(card_id)
                        },
                        disabled=True
                    )],
                    style={'textAlign': 'center'})
            ], style={'marginTop': '10px', 'marginRight': '10px', 'whiteSpace': 'pre-line'}, className='card')
        ], className='')
        for card_id in cards_values_df['type_id_int'].drop_duplicates()
    ], className= 'container')

    return cards


layout = html.Div(
        id='page1', 
        children = [
            html.Div([
                html.Div( 
                    children=[
                        html.Content(
                            id='items', 
                            children=[
                                dbc.ListGroup(id='show_list', style={'marginTop': '10px', 'marginLeft': '10px'})
                            ]
                        )
                    ], 
                    className='two columns'
                ),

                html.Div([
                    html.Div([
                        dbc.CardColumns(id='show_cards')
                    ], style={'marginRight': '15px'})
                ], className='nine columns')
            ], className='row flex-display'),
            html.Div(id= 'go_to_details', children=[
                html.Div(
                    dcc.Link(
                        dbc.Button(
                            "Show Details", outline=True, color="secondary", className="mr-1"
                        ),
                        href='/subtraction-details', 
                        style={'float': 'right', 'margin': '40px 30px 0 0'}, 
                        id='details_btn', 
                ))
            ], style={'display': 'none'}),
            html.H3(id='test_output')
        ])


@app.callback(
    Output('show_list', 'children'),
    Output('show_cards', 'children'),
    Input('input_data', 'data'), 
)
def show_page(input_data): 
    input_data = input_data or {}

    if not input_data:
        raise PreventUpdate
    listgroup_values_df = pd.DataFrame.from_dict(input_data['initial'].get('listgroup_values', []))
    cards_values_df = pd.DataFrame.from_dict(input_data['initial'].get('cards_values', []))

    return show_items(listgroup_values_df, True), show_cards(cards_values_df)
    
@app.callback(
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
    Output('items', 'children'),
    Output({'id': 'card_value', 'index': ALL}, 'options'),
    Input({'id': 'card_value', 'index': ALL}, 'value'),
    State({'id': 'card_value', 'index': ALL}, 'options'),
    State('input_data', 'data'),
)
def substruct_if_clicked(card_values, card_options, input_data):
    input_data = input_data or {}
    if not input_data or not card_options: 
        raise PreventUpdate
    
    btns_visibility = []
    selected_vals = {}
    for i, opts in enumerate(card_values):
        if opts:
            selected_vals[i] = [card_options[i][opt_idx]['label'] for opt_idx in opts]
            if len(opts) == len(card_options[i]):
                btns_visibility.append(False)
            else: 
                btns_visibility.append(True)
        else: 
            btns_visibility.append(True)
        
    current_listgroup = input_data['initial']['listgroup_values']
    cards_values_all = input_data['initial']['cards_values']

    #new_items, new_card_options =  hlp.subtract_selected_v2(current_listgroup, cards_values_all, selected_vals, card_options)

    new_items, new_card_options =  hlp.subtract_selected_v3(current_listgroup, cards_values_all, selected_vals, card_options, card_values)
    return btns_visibility, show_items(new_items, False), new_card_options



@app.callback(
    Output('historical_subtraction', 'data'),
    Output('go_to_details', 'style'),
    Output({'id': 'card', 'index': ALL}, 'style'),
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    State('input_data', 'data'),
    State('historical_subtraction', 'data'),
    State({'id': 'card', 'index': ALL}, 'style'),
    State({'id': 'card_value', 'index': ALL}, 'value'),
)
def subtract_handler(n_clicks, input_data, historical_subtraction, card_style, card_values):
    if not [click for click in n_clicks if click] or not input_data: 
        raise PreventUpdate
    
    historical_subtraction = historical_subtraction or {}
    
    callback = dash.callback_context.triggered[0]['prop_id'].split('.')
    clicked_btn = callback[0]
    clicked_btn = json.loads(clicked_btn)
    clicked_btn_index = clicked_btn.get('index', None)
    cards_values_all = input_data['initial']['cards_values']
    
    cards_subtraction_details = historical_subtraction.get('cards_subtraction_details', [])

    historical_subtraction['cards_subtraction_details'] = hlp.commit_subtraction_v2(
        clicked_btn_index, cards_values_all, cards_subtraction_details, card_values
    )
    
    # Update components visibility
    display_details_btn = {'display': 'none'}
    if historical_subtraction['cards_subtraction_details']:
        display_details_btn = {'display': 'block'}
    
    card_style[clicked_btn_index]['pointer-events'] = 'none'
    card_style[clicked_btn_index]['visibility'] = 'hidden'
    card_style[clicked_btn_index]['opacity'] = '0'
    #card_style[clicked_btn_index]['transition']= 'visibility 8s, opacity 8s linear'

    return historical_subtraction, display_details_btn, card_style

