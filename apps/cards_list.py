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
from apps.fnc_container import crud_op_db, helpers as hlp
from apps.fnc_container import components as components
from datetime import datetime
from flask_login import current_user


def show_items(listgroup_values, mainCallBack=True):
    listgroup_values = listgroup_values.sort_values(by=['type'])
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
            if x['selected'] == 0
            #if x['production'] > 0 or x['available_quantity'] > 0
        ]
    return dbc.ListGroup(id='show_list', children=[
        dbc.ListGroupItem(
            children=[
                dbc.Button(
                            hlp.type_line_break(x, True),
                            className='listItemBtn',
                            id={'id': 'lst_item_btn',
                                'index': x['type_id_str']},
                )
            ]
        )
        for i, x in listgroup_values.iterrows()
        if x['production'] > 0 or x['available_quantity'] > 0
    ])


def show_cards(cards_values_df):
    def build_card_header(card_id):
        card = cards_values_df.loc[cards_values_df['type_id_int'] == card_id]
        card_time = f'{card["card_time"].values[0]}'
        waitress = f'{card["waitress"].values[0]}'
        process = f'{card["process"].values[0]}'
        header = html.Div([
            html.P(process),
            html.P(waitress),
            html.P(card_time),
        ], id='card_head')

        return header

    cards = html.Div([
        html.Div(
            html.Div(
                id={
                    'id': 'card_container',
                    'index': int(card_id)
                },
                children=[
                    dbc.Card(id={
                        'id': 'card',
                        'index': int(card_id)
                    }, children=[
                        dbc.CardHeader(build_card_header(card_id)),
                        dbc.CardBody(
                            id={
                                'id': 'card_body',
                                'index': int(card_id)
                            },
                            children=[
                                html.Div([
                                    dbc.Checklist(
                                        id={
                                            'id': 'card_value',
                                            'index': f'{int(card_id)}_{i}'
                                        },
                                        options=hlp.create_checkbox_opt(cards_values_df.loc[
                                            # & (cards_values_df['gang_number'] == number)
                                            (cards_values_df['type_id_int'] == card_id)
                                        ]),
                                        value=[],
                                        labelCheckedStyle={
                                            "textDecoration": 'line-through',
                                        },
                                        className='hidden_box',
                                        labelStyle={},

                                    )])
                            ],
                            className='disabled'
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
                                disabled=False
                            )],
                            style={'textAlign': 'center'})
                    ], style={'marginTop': '10px', 'marginRight': '10px', 'whiteSpace': 'pre-line'}, className='card')
            ], className='example--item'),  # , style={'width': '340px'}
            className='.has-row-10'
        )
        for i, card_id in enumerate(cards_values_df['type_id_int'].drop_duplicates())
    ], className='grid has-cols-1 is-dense has-cols-xs-1 has-cols-sm-2 has-cols-md-3 has-cols-lg-4')

    return cards


layout = html.Div(
    id='page1',
    children=[
        components.filter_modal,
        html.Div(children=[
            html.Div(id='no_data'),
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
                    html.Div(id='show_cards'), 
                    html.Div(
                        html.Div([
                                html.A('❮', style={'marginRight': '5px'}, id='prev', n_clicks=0), 
                                html.A('❯', id='next', style={'marginRight': '5px'}, n_clicks=0),
                                html.A('Show All', id='show_all', n_clicks=0)
                            ], className='pagination')
                    )
                ], className='nine columns')
            ], className='row flex-display'),

        ]),
    ])


# Fetch data from our database
@app.callback(
    Output('input_data', 'data'),
    Output('pagination_status', 'data'),
    Output('no_data', 'children'),
    Input('url', 'pathname'), 
    Input('prev', 'n_clicks'),
    Input('next', 'n_clicks'),
    Input('show_all', 'n_clicks'),
    Input('filtred_cards_tmp', 'data'),
    State('pagination_status', 'data'),
    prevent_initial_call=True
)
def fetch_data(pathname, prev, next, show_all, filtred_cards, pagination_status):
    call_context = dash.callback_context.triggered[0]
    context = call_context['prop_id'].split('.')[0]
    if call_context['prop_id'] == 'filtred_cards_tmp.data':
        if filtred_cards: 
            cards = pd.DataFrame.from_dict(filtred_cards['food'])
            return {
                'metadata': {
                    'filter': 'filtred_cards_tmp'
                },
                'data': {
                    'cards_values': cards.to_dict('records')
                }
            }, pagination_status, ''
        else: 
            raise PreventUpdate

    elif not 'url' in call_context['prop_id'] and call_context['value'] > 0: 

        if context == 'next': 
            # Get the next 10 cards
            cards_df = crud_op_db.read_food_cards(id_int=pagination_status['last_id'])
            if not cards_df.empty:
                left_list_df = hlp.foods_listing(cards_df)
                pagination_status = {
                    'first_id': pagination_status['last_id'],
                    'last_id': max(cards_df['type_id_int'])
                }
                return {
                    'metadata': {
                        'filter': False
                    },
                    'data': {
                            'cards_values': cards_df.to_dict('records')
                        }}, pagination_status, ''

        elif context == 'prev': 
            # get the previous 10 cards
            cards_df = crud_op_db.read_food_cards(
                id_int=pagination_status['first_id'], 
                next=False
            )
            if not cards_df.empty:
                left_list_df = hlp.foods_listing(cards_df)
                pagination_status = {
                    'first_id': min(cards_df['type_id_int']),
                    'last_id': max(cards_df['type_id_int'])
                }
                return {
                    'metadata': {
                        'filter': False
                    },
                    'data': {
                        'cards_values': cards_df.to_dict('records')
                        }}, pagination_status, ''

        elif context == 'show_all': 
            cards_df = crud_op_db.read_food_cards(show_all=True)
            if not cards_df.empty:
                left_list_df = hlp.foods_listing(cards_df)
                pagination_status = {
                    'first_id': min(cards_df['type_id_int']),
                    'last_id': max(cards_df['type_id_int'])
                }
                return {
                    'metadata': {
                        'filter': False
                    },
                    'data': {
                        'cards_values': cards_df.to_dict('records')
                        }}, pagination_status, ''
            
        raise PreventUpdate

    if pathname == '/items-selection' and current_user.is_authenticated:
        cards_df = crud_op_db.read_food_cards()
        
        if not cards_df.empty:
            left_list_df = hlp.foods_listing(cards_df)
            pagination_status = {
                'first_id': min(cards_df['type_id_int']),
                'last_id': max(cards_df['type_id_int'])
            }
            return {
                'metadata': {
                        'filter': False
                    },
                'data': {
                    'cards_values': cards_df.to_dict('records')
                    }}, pagination_status, ''
        else: 
            return {}, {}, components.no_data_toast()
    else:
        raise PreventUpdate


@app.callback(
    Output('show_cards', 'children'),
    Input('input_data', 'data')
)
def show_page(input_data):
    context = dash.callback_context.triggered
    if context[0]['prop_id'] == '.':
        raise PreventUpdate
    if not input_data:
        raise PreventUpdate
    
    input_data = input_data or {}
    cards_values_df = pd.DataFrame.from_dict(input_data['data'].get('cards_values', []))

    return show_cards(cards_values_df)

# left list items controller
@app.callback(
    Output('show_list', 'children'),
    Output('food_tracer', 'data'),
    Input('input_data', 'data'), 
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    Input({'id': 'card_value', 'index': ALL}, 'value'),
    Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'),
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'children'),
    State('food_tracer', 'data')
)
def update_list_items(input_data, start_btn, card_value, lst_item_btn, start_btn_status, food_tracer):
    context = dash.callback_context.triggered
    input_data = input_data or {'data': {}}
    current_cards = pd.DataFrame.from_dict(input_data['data'].get('cards_values'))
    food_tracer = food_tracer or crud_op_db.init_cards_tracer() 
    if not food_tracer: 
        raise PreventUpdate
    food_tracer = pd.DataFrame.from_dict(food_tracer)
    cntxt = context[0].get('prop_id', None)

    if 'commit_substraction_btn' in cntxt and len(context) == 1: 
        context_dict = json.loads(cntxt.split('.')[0])
        type_id_int = int(context_dict['index'].split('_')[0])
        card_idx = int(context_dict['index'].split('_')[1])
        if start_btn_status[card_idx] == 'Start':
            food_tracer = hlp.update_production(
                food_tracer,
                type_id_int
            )
            new_cards = hlp.intersection(current_cards, food_tracer)
            new_list = hlp.foods_listing(new_cards)

            return show_items(new_list, True), food_tracer.to_dict('records')

    new_cards = hlp.intersection(current_cards, food_tracer)
    new_list = hlp.foods_listing(new_cards)

    if 'card_value' in cntxt and len(context) == 1: 
        food_tracer = hlp.insert_selected_item(food_tracer, context)
        new_cards = hlp.intersection(current_cards, food_tracer)
        new_list = hlp.foods_listing(new_cards)
        return show_items(new_list, True), food_tracer.to_dict('records')
    
    if  'lst_item_btn' in cntxt and len(context) == 1:
        new_cards = hlp.intersection(current_cards, food_tracer)
        food_tracer = hlp.insert_selected_item_2(food_tracer, context, new_cards)
        new_cards = hlp.intersection(current_cards, food_tracer)
        new_list = hlp.foods_listing(new_cards)
        return show_items(new_list, True), food_tracer.to_dict('records')

    return show_items(new_list, True), food_tracer.to_dict('records')


@app.callback(
    Output({'id': 'card_value', 'index': ALL}, 'value'),
    Output({'id': 'card_body', 'index': ALL}, 'className'),
    Output({'id': 'card', 'index': ALL}, 'className'),
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'color'),
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'children'),
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
    Input('food_tracer', 'data'), 
    State('input_data', 'data'),
    State({'id': 'card_body', 'index': ALL}, 'className'), 
    State({'id': 'card', 'index': ALL}, 'className'), 
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'color'),
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'children'),
    State({'id': 'card_value', 'index': ALL}, 'value'),
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
)
def card_style(food_tracer, input_data, current_body_style, current_card_style, btns_color, btns_text, card_value, stop_btns):
    context = dash.callback_context.triggered
    if not food_tracer: 
        raise PreventUpdate
    
    # Match food_tracer with input_data (get the same type_id_int/order)
    input_data = input_data or {'data':{}}
    current_cards = pd.DataFrame.from_dict(input_data['data'].get('cards_values'))
    food_tracer = pd.DataFrame.from_dict(food_tracer)
    cards_status = hlp.intersection(current_cards, food_tracer)
    cards_status_grp = cards_status.groupby(['type_id_int']).agg({
        'available_quantity': 'sum',
        'type_only': 'last',
        'bonus': 'last',
        'production': 'sum'
    }).reset_index(drop=True)
    for idx, row in cards_status_grp.iterrows(): 
        if row['production']:
            current_body_style[idx] = 'enable_card'
            current_card_style[idx] = 'active_card'
            btns_color[idx] = 'danger'
            btns_text[idx] = 'Stop'
            stop_btns[idx] = True
        else: 
            current_body_style[idx] = 'disabled'
            current_card_style[idx] = ''
            btns_color[idx] = 'success'
            btns_text[idx] = 'Start'
    for idx, (i, row) in enumerate(cards_status.drop_duplicates(subset='type_id_int').iterrows()):
        card_items = cards_status.loc[cards_status['type_id_int']==row['type_id_int']]
        card_value[idx] = card_items.loc[card_items['selected']==1]['type_id_str'].tolist()
        if len(card_value[idx]) == len(card_items):
            stop_btns[idx] = False
            
    return card_value, current_body_style, current_card_style, btns_color, btns_text, stop_btns


@app.callback(
    Output({'id': 'card_container', 'index': ALL}, 'className'),
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    State('input_data', 'data'),
    State({'id': 'card_container', 'index': ALL}, 'className'),
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'children'),
    State({'id': 'card_value', 'index': ALL}, 'value'),
)
def subtract_handler(n_clicks, input_data, card_container, button_children_status, card_value):
    if not [click for click in n_clicks if click] or not input_data:
        raise PreventUpdate

    callback = dash.callback_context.triggered[0]['prop_id'].split('.')
    clicked_btn = callback[0]
    clicked_btn = json.loads(clicked_btn)
    clicked_btn_index = clicked_btn.get('index', None)

    if button_children_status[int(clicked_btn_index.split('_')[1])] == 'Stop':
        cards_values_all = pd.DataFrame.from_dict(input_data['data']['cards_values'])
        type_id_int = int(clicked_btn_index.split('_')[0])
        card_food = cards_values_all.loc[cards_values_all['type_id_int'] == type_id_int]
        if len(card_value[int(clicked_btn_index.split('_')[1])]) == len(card_food):
            # Update "food" and "historical_sales" tables ...
            crud_op_db.update_vals(card_food)
            card_container[int(clicked_btn_index.split('_')[1])] = 'destroy_card'

    return card_container


@app.callback(
    Output("filter_modal", "is_open"),
    Input("btn_filter_modal", "n_clicks"),
    Input("apply_filter", "n_clicks"),
    State("filter_modal", "is_open"),
)
def toggle_modal(
    n1,
    n2,
    is_open,
):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    context_value = dash.callback_context.triggered[0]['value']

    if context == 'btn_filter_modal' and context_value:
        return not is_open
    if context == 'apply_filter' and context_value:
        return not is_open
    return is_open

@app.callback(
    Output('filter_options', 'data'),
    Input('btn_filter_modal', 'n_clicks')
)
def update_filter_options(btn_filter_modal): 
    if btn_filter_modal:
        data = crud_op_db.update_filter_options('food') 
        result = {'foods': data.to_dict('records')}
        return result
    return None

@app.callback(
    Output('filtred_cards_tmp', 'data'),
    Output('date_picker_1', 'options'),
    Output('datetime_picker_1', 'options'),
    Output('process_1', 'options'),
    Output('gang_number_1', 'options'),
    Output('plate_type_1', 'options'),
    Output('phrase_1', 'options'),
    Input('date_picker_1', 'value'),
    Input('datetime_picker_1', 'value'),
    Input('process_1', 'value'),
    Input('gang_number_1', 'value'),
    Input('plate_type_1', 'value'),
    Input('phrase_1', 'value'),
    Input('filter_options', 'data'),
    Input('apply_filter', 'n_clicks'),
    State('date_picker_1', 'options'),
    State('datetime_picker_1', 'options'),
    State('process_1', 'options'),
    State('gang_number_1', 'options'),
    State('plate_type_1', 'options'),
    State('phrase_1', 'options'),
    State('sort_by', 'value'),
    State('sort_how', 'value'),
)
def update_result(
    selected_dates,
    selected_datetime,
    selected_cards,
    selected_gang_numbers,
    selected_plates,
    selected_phrases,
    filter_options,
    apply_filter,
    date_picker_options,
    datetime_picker_options,
    process_options,
    gang_number_options,
    plate_type_options,
    phrase_options,
    sort_by, 
    sort_how
):

    filter_options = filter_options or {}

    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if not filter_options:
        raise PreventUpdate

    cards_values = pd.DataFrame.from_dict(filter_options.get('foods'))

    cards_subtr = cards_values.copy()
    #cards_subs_copy = cards_subtr.copy()

    if selected_dates:
        cards_subtr = cards_subtr.query('card_date in @selected_dates')

    if selected_datetime:
        cards_subtr = cards_subtr.query('card_time in @selected_datetime')

    if selected_cards:
        cards_subtr = cards_subtr.query('process in @selected_cards')

    if selected_gang_numbers:
        #cards_subtr = cards_subtr.query('type_id_str in @selected_plates')
        gang_numbers = cards_subtr.loc[cards_subtr['gang_number'].isin(
            selected_gang_numbers)]['type_id_int'].drop_duplicates()
        cards_subtr = cards_subtr.loc[cards_subtr['type_id_int'].isin(
            gang_numbers)]

    if selected_plates:
        #cards_subtr = cards_subtr.query('type_id_str in @selected_plates')
        type_id_int = cards_subtr.loc[cards_subtr['type_id_str'].isin(
            selected_plates)]['type_id_int'].drop_duplicates()
        cards_subtr = cards_subtr.loc[cards_subtr['type_id_int'].isin(
            type_id_int)]

    if selected_phrases:
        cards_subtr = cards_subtr.query('waitress in @selected_phrases')

    # date_picker: update options
    if context != 'date_picker_1' or len(dash.callback_context.triggered) > 1:
        date_picker_options = [{'value': x, 'label': x}
                               for x in cards_subtr['card_date'].drop_duplicates()]
        if not selected_cards and not selected_plates and not selected_phrases and not selected_datetime and not selected_gang_numbers:
            date_picker_options = [{'value': x, 'label': x}
                                   for x in cards_values['card_date'].drop_duplicates()]

    # datetime_picker_1: update options
    if context != 'datetime_picker_1':
        datetime_picker_options = [{'value': x, 'label': x}
                                   for x in cards_subtr['card_time'].drop_duplicates()]
        if not selected_cards and not selected_plates and not selected_phrases and not selected_dates and not selected_gang_numbers:
            datetime_picker_options = [{'value': x, 'label': x}
                                       for x in cards_values['card_time'].drop_duplicates()]

    # process: update options
    if context != 'process_1':
        process_options = [{'value': x, 'label': x}
                           for x in cards_subtr['process'].drop_duplicates()]
        if not selected_dates and not selected_plates and not selected_phrases and not selected_datetime and not selected_gang_numbers:
            process_options = [{'value': x, 'label': x}
                               for x in cards_values['process'].drop_duplicates()]

    # gang_number_1: update options
    if context != 'gang_number_1':
        gang_number_options = [{'value': x, 'label': x}
                               for x in cards_subtr['gang_number'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_phrases and not selected_datetime and not selected_plates:
            gang_number_options = [{'value': x, 'label': x}
                                   for x in cards_values['gang_number'].drop_duplicates()]

    # plate_type: update options
    if context != 'plate_type_1':
        plate_type_options = [{'value': x['type_id_str'], 'label': x['type_only']}
                              for i, x in cards_subtr.drop_duplicates(subset=['type_id_str']).iterrows()]
        if not selected_cards and not selected_dates and not selected_phrases and not selected_datetime and not selected_gang_numbers:
            [{'value': x['type_id_str'], 'label': x['type_only']}
                for i, x in cards_subtr.drop_duplicates(subset=['type_id_str']).iterrows()]

    # phrase: update options
    if context != 'phrase_1':
        phrase_options = [{'value': x, 'label': x}
                          for x in cards_subtr['waitress'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_plates and not selected_datetime and not selected_gang_numbers:
            phrase_options = [{'value': x, 'label': x}
                              for x in cards_values['waitress'].drop_duplicates()]

    cards_subtr = cards_subtr.sort_values(
        by=['type_id_int', 'gang_number']).reset_index(drop=True)

    cards_subtr = cards_subtr.sort_values(by=sort_by, ascending=sort_how).reset_index(drop=True)
    filter_options['food'] = cards_subtr.to_dict('records')
    if context != 'apply_filter' or not apply_filter: 
        filter_options = None

    return filter_options, date_picker_options, datetime_picker_options, process_options, gang_number_options, plate_type_options, phrase_options
