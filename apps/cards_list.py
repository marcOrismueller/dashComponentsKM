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
from apps.fnc_container import components as components
from datetime import datetime

def show_items(listgroup_values, mainCallBack=True):
    if mainCallBack:
        return [
            dbc.ListGroupItem(
                children=[
                    dbc.Button(
                            hlp.type_line_break(x, 'btns'),
                            className='listItemBtn',
                            id={'id': 'lst_item_btn', 'index': x['type_id_str']},
                        )
                ], 
            )
            for i, x in listgroup_values.iterrows()
            if x['quantity'] > 0
        ]

    return dbc.ListGroup(id='show_list', children=[
        dbc.ListGroupItem(
            children=[
                dbc.Button(
                            hlp.type_line_break(x, True),
                            className='listItemBtn',
                            id={'id': 'lst_item_btn', 'index': x['type_id_str']},
                        )
            ]
        )
        for i, x in listgroup_values.iterrows()
        if x['quantity'] > 0
    ])



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
                        html.Div([
                            dbc.Checklist(
                                id={
                                    'id': 'card_value',
                                    'index': f'{int(card_id)}_{i}'
                                },
                                options=hlp.create_checkbox_opt(cards_values_df.loc[
                                        (cards_values_df['type_id_int'] == card_id) #& (cards_values_df['gang_number'] == number)
                                    ]),
                                value=[],
                                labelCheckedStyle={
                                    "textDecoration": 'line-through',
                                    },
                                className='hidden_box',
                                labelStyle={},
                                
                            )])
                    ],
                ),

                dbc.CardFooter([
                    dbc.Button(
                        "Start",
                        color='success', 
                        size="lg",
                        className='m-4',
                        id={
                            'id': 'commit_substraction_btn',
                            'index': f'{int(card_id)}_{i}'
                        },
                        disabled=True
                    )],
                    style={'textAlign': 'center'})
            ], style={'marginTop': '10px', 'marginRight': '10px', 'whiteSpace': 'pre-line'}, className='card')
        ]) #, style={'width': '340px'}
        
        for i, card_id in enumerate(cards_values_df['type_id_int'].drop_duplicates())
    ], className= 'grid-container')

    return cards


layout = html.Div(
        id='page1',
        children = [
            components.filter_modal,
            html.Div(children=[
                html.Div([
                    html.Div(
                        children=[
                            html.Content(
                                id='items',
                                children=[
                                    dbc.ListGroup(id='show_list')
                                ]
                            )
                        ],
                        className='two columns', style={'marginTop': '12px'}
                    ),

                    html.Div([
                        html.Div([
                            dbc.CardColumns(id='show_cards')
                        ])
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
            ]),
            html.Div(id='gang_test')
        ])

@app.callback(
    Output('show_list', 'children'),
    Output('show_cards', 'children'),
    Output('gang_notifier', 'data'),
    Input('input_data', 'data'),
    Input('filtred_cards', 'data')
)
def show_page(input_data, filtred_cards): #, filtred_cards
    context = dash.callback_context.triggered
    if context[0]['prop_id'] == '.': 
        raise PreventUpdate
    if not input_data: 
            raise PreventUpdate

    #input_data = input_data or {}
    input_data = input_data or {}

    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    context_value = dash.callback_context.triggered[0]['value']
    if context == 'filtred_cards' and context_value: 
        input_data = filtred_cards
    
    listgroup_values_df = pd.DataFrame.from_dict(input_data['initial'].get('listgroup_values', []))
    cards_values_df = pd.DataFrame.from_dict(input_data['initial'].get('cards_values', []))
    gang_notifier = {}
    for i, card_id in enumerate(cards_values_df['type_id_int'].drop_duplicates()): 
        gang_notifier[f'{card_id}_{i}'] = []
    return show_items(listgroup_values_df, True), show_cards(cards_values_df), gang_notifier

@app.callback(
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
    Output('items', 'children'),
    Output({'id': 'card_value', 'index': ALL}, 'options'),
    Output('substruct_if_clicked', 'data'),
    Input({'id': 'card_value', 'index': ALL}, 'value'),
    Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'),
    State({'id': 'card_value', 'index': ALL}, 'options'),
    State('input_data', 'data'),
    State('filtred_cards', 'data'),
    State('substruct_if_clicked', 'data'), 
    State('gang_notifier', 'data')
)
def substruct_if_clicked(card_values, lst_item_btn, card_options, input_data, filtred_cards, substruct_if_clicked, gang_notifier): #, filtred_cards
    context = dash.callback_context.triggered[0]
  
    if not card_values or context['value'] is None or context['prop_id'] == '.': 
        raise PreventUpdate
    substruct_if_clicked = substruct_if_clicked or gang_notifier
 
    if not set(substruct_if_clicked.keys()) == set(gang_notifier.keys()): 
        substruct_if_clicked = gang_notifier

    input_data = input_data or {}
    
    if filtred_cards: 
        input_data = filtred_cards
    
    if not input_data or not card_options:
        raise PreventUpdate
    btns_visibility = []
    selected_vals = {}
    

    current_listgroup = input_data['initial']['listgroup_values']
    cards_values_all = input_data['initial']['cards_values']
    
    prop_id = json.loads(context['prop_id'].split('.')[0])

    if prop_id['id'] == 'card_value':

        substruct_if_clicked = hlp.get_gang_subelements(cards_values_all, substruct_if_clicked, context['value'], prop_id['index'])
        
    if prop_id['id'] == 'lst_item_btn': 
        for ids in substruct_if_clicked: 
            substruct_if_clicked[ids] = card_values[int(ids.split('_')[1])]
    
    new_items, new_card_options =  hlp.subtract_selected_v3(current_listgroup, cards_values_all, selected_vals, card_options, card_values, substruct_if_clicked)
    
    for i, opts in enumerate(card_values):
        idx = [x for x in list(substruct_if_clicked.keys()) if f'_{i}' in x]
        current_vals = substruct_if_clicked.get(idx[0], [])
        if opts:
            if len(current_vals) == len(card_options[i]):
                btns_visibility.append(False)
            else:
                btns_visibility.append(True)
        else:
            btns_visibility.append(True)
    
    return btns_visibility, show_items(new_items, False), new_card_options, substruct_if_clicked


@app.callback(
    Output({'id': 'card_value', 'index': ALL}, 'value'), 
    Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'), 
    State({'id': 'card_value', 'index': ALL}, 'value'), 
    State({'id': 'card_value', 'index': ALL}, 'options'),
    State('input_data', 'data'),
    State('substruct_if_clicked', 'data')
)
def substruct_if_list_clicked(lst_item_btn, card_values, card_options, input_data, substruct_if_clicked): 
    context = None
    context = dash.callback_context.triggered[0]
    if not substruct_if_clicked: 
        return card_values
    
    try:
        context = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])    
        context_value = dash.callback_context.triggered[0]['value']
        if context['id']=='lst_item_btn' and not context_value:
            #print(substruct_if_clicked)
            for idx in substruct_if_clicked: 
                card_values[int(idx.split('_')[-1])] = substruct_if_clicked[str(idx)]
                card_values[int(idx.split('_')[-1])] = list(dict.fromkeys(card_values[int(idx)]))
            
            return card_values
    except: 
        try: 
            for idx in substruct_if_clicked: 
                card_values[int(idx.split('_')[-1])] = substruct_if_clicked[str(idx)]
        except: 
            pass
        return card_values

    if context: 
        card_values = hlp.click_list_handler(card_values, card_options, context, input_data)
    
    return card_values


@app.callback(
    Output('historical_subtraction', 'data'),
    Output('go_to_details', 'style'),
    Output({'id': 'card', 'index': ALL}, 'style'),
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'color'), 
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'children'), 
    #Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    State('input_data', 'data'),
    State('historical_subtraction', 'data'),
    State({'id': 'card', 'index': ALL}, 'style'),
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'color'), 
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'children')
)
def subtract_handler(n_clicks, input_data, historical_subtraction, card_style, button_color_status, button_children_status):
    if not [click for click in n_clicks if click] or not input_data:
        raise PreventUpdate
    historical_subtraction = historical_subtraction or {}

    callback = dash.callback_context.triggered[0]['prop_id'].split('.')
    clicked_btn = callback[0]
    clicked_btn = json.loads(clicked_btn)
    clicked_btn_index = clicked_btn.get('index', None)
    display_details_btn = {'display': 'none'}

    if button_children_status[int(clicked_btn_index.split('_')[1])] == 'Start':
        cards_values_all = input_data['initial']['cards_values']
        cards_subtraction_details = historical_subtraction.get('cards_subtraction_details', [])
        # Commit the subtraction only if "Stop btn" clicked
        historical_subtraction['cards_subtraction_details'] = hlp.commit_subtraction_v2(
            int(clicked_btn_index.split('_')[0]), cards_values_all, cards_subtraction_details
        )

        button_children_status[int(clicked_btn_index.split('_')[1])] = 'Stop'
        button_color_status[int(clicked_btn_index.split('_')[1])] = 'danger'
        card_style[int(clicked_btn_index.split('_')[1])]['border'] = '3px #0dc400 solid'
    else:
        card_style[int(clicked_btn_index.split('_')[1])]['pointer-events'] = 'none'
        card_style[int(clicked_btn_index.split('_')[1])]['visibility'] = 'hidden'
        card_style[int(clicked_btn_index.split('_')[1])]['opacity'] = '0'
        if historical_subtraction['cards_subtraction_details']:
            display_details_btn = {'display': 'block'}


    return historical_subtraction, display_details_btn, card_style, button_color_status, button_children_status

@app.callback(
    Output("filter_modal", "is_open"),
    Output('filtred_cards', 'data'),
    Input("btn_filter_modal", "n_clicks"), 
    Input("apply_filter", "n_clicks"),
    State("filter_modal", "is_open"),
    State('filtred_cards_tmp', 'data'), 
    State('sort_by', 'value'),
    State('sort_how', 'value'),
)
def toggle_modal(
        n1, 
        n2, 
        is_open, 
        filtred_cards_tmp, 
        sort_by, 
        sort_how, 
    ):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    context_value = dash.callback_context.triggered[0]['value']

    if context == 'btn_filter_modal' and context_value:
        return not is_open, {}

    if context == 'apply_filter' and context_value: 
        df = pd.DataFrame.from_dict(filtred_cards_tmp['initial']['cards_values'])
        sort_by = [sort_by]
        ascending = False
        if sort_how == 0:
            ascending = True
        
        df = df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
        filtred_cards_tmp['initial']['cards_values'] = df.to_dict('records')
        return not is_open, filtred_cards_tmp
    return is_open, {}

@app.callback(
    Output('filtred_cards_tmp', 'data'),
    Output('date_picker_1', 'options'), 
    Output('datetime_picker_1', 'options'),
    Output('card_index_1', 'options'),  
    Output('gang_number_1', 'options'),
    Output('plate_type_1', 'options'), 
    Output('phrase_1', 'options'), 
    Input('date_picker_1', 'value'), 
    Input('datetime_picker_1', 'value'),
    Input('card_index_1', 'value'),
    Input('gang_number_1', 'value'),
    Input('plate_type_1', 'value'),
    Input('phrase_1', 'value'),
    Input('input_data', 'data'),
    State('date_picker_1', 'options'),
    State('datetime_picker_1', 'options'),
    State('card_index_1', 'options'),
    State('gang_number_1', 'options'),
    State('plate_type_1', 'options'),
    State('phrase_1', 'options'),
)
def update_result(
        selected_dates, 
        selected_datetime,
        selected_cards, 
        selected_gang_numbers,
        selected_plates, 
        selected_phrases, 
        input_data,
        date_picker_options, 
        datetime_picker_options, 
        card_index_options, 
        gang_number_options,
        plate_type_options, 
        phrase_options, 
    ):
    
    input_data = input_data or {}

    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    if not input_data:
        raise PreventUpdate
    
    cards_values = pd.DataFrame.from_dict(
            input_data['initial'].get('cards_values')
        )
    
    cards_subtr = cards_values.copy()
    #cards_subs_copy = cards_subtr.copy()

    if selected_dates: 
        cards_subtr = cards_subtr.query('card_date in @selected_dates')

    if selected_datetime: 
        cards_subtr = cards_subtr.query('card_time in @selected_datetime')

    if selected_cards: 
        cards_subtr = cards_subtr.query('card_index in @selected_cards')

    if selected_gang_numbers: 
        #cards_subtr = cards_subtr.query('type_id_str in @selected_plates')
        gang_numbers = cards_subtr.loc[cards_subtr['gang_number'].isin(selected_gang_numbers)]['type_id_int'].drop_duplicates()
        cards_subtr = cards_subtr.loc[cards_subtr['type_id_int'].isin(gang_numbers)]

    if selected_plates: 
        #cards_subtr = cards_subtr.query('type_id_str in @selected_plates')
        type_id_int = cards_subtr.loc[cards_subtr['type_id_str'].isin(selected_plates)]['type_id_int'].drop_duplicates()
        cards_subtr = cards_subtr.loc[cards_subtr['type_id_int'].isin(type_id_int)]

    if selected_phrases: 
        cards_subtr = cards_subtr.query('card_phrase in @selected_phrases')

    # date_picker: update options
    if context != 'date_picker_1' or len(dash.callback_context.triggered) > 1: 
        date_picker_options = [{'value': x, 'label': x} for x in cards_subtr['card_date'].drop_duplicates()]
        if not selected_cards and not selected_plates and not selected_phrases and not selected_datetime and not selected_gang_numbers: 
            date_picker_options = [{'value': x, 'label': x} for x in cards_values['card_date'].drop_duplicates()]

    # datetime_picker_1: update options
    if context != 'datetime_picker_1':
        datetime_picker_options = [{'value': x, 'label': x} for x in cards_subtr['card_time'].drop_duplicates()]
        if not selected_cards and not selected_plates and not selected_phrases and not selected_dates and not selected_gang_numbers: 
            datetime_picker_options = [{'value': x, 'label': x} for x in cards_values['card_time'].drop_duplicates()]

    # card_index: update options
    if context != 'card_index_1':
        card_index_options = [{'value': x, 'label': x} for x in cards_subtr['card_index'].drop_duplicates()]
        if not selected_dates and not selected_plates and not selected_phrases and not selected_datetime and not selected_gang_numbers: 
            card_index_options = [{'value': x, 'label': x} for x in cards_values['card_index'].drop_duplicates()]

    # gang_number_1: update options
    if context != 'gang_number_1':
        gang_number_options = [{'value': x, 'label': x} for x in cards_subtr['gang_number'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_phrases and not selected_datetime and not selected_plates:
            gang_number_options = [{'value': x, 'label': x} for x in cards_values['gang_number'].drop_duplicates()]


    # plate_type: update options
    if context != 'plate_type_1':
        plate_type_options = [{'value': x['type_id_str'], 'label': x['type_only']} for i, x in cards_subtr.drop_duplicates(subset=['type_id_str']).iterrows()]
        if not selected_cards and not selected_dates and not selected_phrases and not selected_datetime and not selected_gang_numbers:
            [{'value': x['type_id_str'], 'label': x['type_only']} for i, x in cards_subtr.drop_duplicates(subset=['type_id_str']).iterrows()]

    # phrase: update options
    if context != 'phrase_1':
        phrase_options = [{'value': x, 'label': x} for x in cards_subtr['card_phrase'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_plates and not selected_datetime and not selected_gang_numbers:
            phrase_options = [{'value': x, 'label': x} for x in cards_values['card_phrase'].drop_duplicates()]

    input_data['initial']['cards_values'] = cards_subtr.to_dict('records')
    
    return input_data, date_picker_options, datetime_picker_options, card_index_options, gang_number_options, plate_type_options, phrase_options
    

    

