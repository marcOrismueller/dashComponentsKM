import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State, ALL, MATCH, ALLSMALLER 
import json
import dash
from dash.exceptions import PreventUpdate
import json
from app import app
import pandas as pd
from apps.fnc_container import crud_op_db, helpers as hlp
from apps.fnc_container import components as components
from apps.fnc_container import read_files 
from datetime import datetime
from flask_login import current_user
import dash_dangerously_set_inner_html
import datetime
from time import sleep
def not_selected(row, previous_selected):
    selected_card = previous_selected.loc[
        (previous_selected['type_id_int']==int(row['type_id_int'])) &
        (previous_selected['gang_number']==int(row['gang_number'])) &
        (previous_selected['type_id_str']==int(row['type_id_str']))
    ]
    return selected_card.empty


def show_items(listgroup_values, mainCallBack=True):
    listgroup_values = listgroup_values.sort_values(by=['type'])
    if mainCallBack:
        return [
            dbc.ListGroupItem(
                children=[
                    html.Div(
                        hlp.list_items(x),
                    )],
            )
            for i, x in listgroup_values.iterrows()
            if x['selected'] == 0
        ]
    return dbc.ListGroup(id='show_list', children=[
        dbc.ListGroupItem(
            children=[
                html.Div(
                    hlp.type_line_break(x, True),
                    className='listItemBtn',
                    id={
                        'id': 'lst_item_btn',
                        'index': x['type_id_str']
                    },
                )
            ]
        )
        for i, x in listgroup_values.iterrows()
        if x['production'] > 0 or x['available_quantity'] > 0
    ])


def show_cards(cards_values_df):
    previous_selected_df = crud_op_db.get_selected_items()
    previous_selected = hlp.df2list(previous_selected_df)
    onProduction = crud_op_db.get_on_production()
    def build_card_header(card_id):
        card = cards_values_df.loc[cards_values_df['type_id_int'] == card_id][:]
        card_time = f'{card["card_time"].values[0]}'
        waitress = f'{card["waitress"].values[0]}'
        process = f'{card["process"].values[0]}'
        header = html.Div([
            html.P(process),
            html.P(waitress),
            html.P(card_time),
        ], id='card_head')
        return header

    if onProduction.empty: 
        onProduction['type_id_int'] = []

    cards = html.Div([
        html.Div(
            html.Div(
                id={
                    'id': 'card_container',
                    'index': f'{int(card_id)}_{i}_{"_".join(list(cards_values_df[cards_values_df["type_id_int"]==card_id]["type_id_str"]))}'
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
                                'index': f'{int(card_id)}_{i}_{"_".join(list(cards_values_df[cards_values_df["type_id_int"]==card_id]["type_id_str"]))}'
                            },
                            children=[
                                html.Div([
                                    html.Div(
                                        id={
                                            'id': 'card_value', 
                                            'index': f'{int(card_id)}_{i}'
                                        }, 
                                        children=hlp.card_body(
                                            cards_values_df.loc[cards_values_df['type_id_int'] == card_id][:], 
                                            previous_selected
                                        )
                                    )
                                ])
                            ],
                            className = 'enable_card' if card_id in list(onProduction['type_id_int']) else 'disabled' 
                        ),

                        dbc.CardFooter([
                            dbc.Button(
                                'Stop' if card_id in list(onProduction['type_id_int']) else 'Start',
                                color='danger' if card_id in list(onProduction['type_id_int']) else 'success',
                                size="lg",
                                className='m-4',
                                id={
                                    'id': 'commit_substraction_btn',
                                    'index': f'{int(card_id)}_{i}_{"_".join(list(cards_values_df[cards_values_df["type_id_int"]==card_id]["type_id_str"]))}'
                                },
                                disabled=False,
                                n_clicks= 1 if card_id in list(onProduction['type_id_int']) else 0
                            )],
                            style={'textAlign': 'center'})
                    ], style={'marginTop': '10px', 'marginRight': '10px', 'whiteSpace': 'pre-line'}, className='card'), 
                    html.Div(dbc.Popover(
                        [
                            dbc.PopoverHeader("Warning", style={'fontSize': '1.5rem', 'color': 'red', 'fontWeight': 'bold'}),
                            dbc.PopoverBody("Please select all elements!", style={'fontSize': '1.8rem'}),
                        ],
                        id={
                            'id': 'popover', 
                            'index': f'{int(card_id)}_{i}_{"_".join(list(cards_values_df[cards_values_df["type_id_int"]==card_id]["type_id_str"]))}'
                        },
                        is_open=False,
                        target=f'card_{i}',
                        placement='bottom', 
                    ))
            ], className=''), 
            className='.has-row-10', 
            id=f'card_{i}'
        )
        for i, card_id in enumerate(cards_values_df.type_id_int.drop_duplicates())
    ], className='grid has-cols-1 is-dense has-cols-xs-1 has-cols-sm-2 has-cols-md-3 has-cols-lg-4')

    return cards


layout = html.Div(
    id='page1',
    children=[
        components.filter_modal,
        html.Div(children=[
            html.Div(id='no_data'),
            html.Div(
                html.P('Checking for new files in 02:59', id='server-time'),
                className='countdown'
            ),
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

        ], className='cards-list'),
    ])


# using serverside callback
@app.callback(
   Output('server-time', 'children'),
   Output('update_trigger', 'data'),
   Input('get_files_interval', 'n_intervals'),
   Input({'id': 'card_body', 'index': ALL}, 'className')
)
def update_timer(n_intervals, cardBodiesClass):
    context = dash.callback_context.triggered[0]
    mins, secs = divmod(30-(n_intervals%30), 60)
    timer = '{:02d}:{:02d}'.format(mins, secs)
    if 'card_body' in context['prop_id'] and 're_order' in context['value']:
        return f'Checking for new files in {timer}', True
    
    if 30-(n_intervals%30) == 30: 
        # Read the new files 
        res = read_files.update_data()
        return f'Checking for new files in {timer}', res
    return f'Checking for new files in {timer}', False
    

# Fetch data from our database
@app.callback(
    Output('input_data', 'data'),
    Output('pagination_status', 'data'),
    Input('update_trigger', 'data'), 
    Input('url', 'pathname'), 
    Input('prev', 'n_clicks'),
    Input('next', 'n_clicks'),
    Input('show_all', 'n_clicks'),
    Input({'id': 'card_container', 'index': ALL}, 'className'),
    Input('filtred_cards_tmp', 'data'),
    State('pagination_status', 'data'),
    State({'id': 'card_body_value', 'index': ALL}, 'n_clicks'),
    State({'id': 'card_body_value', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def fetch_data(update_trigger, pathname, prev, next, show_all, cardContainerClass, filtred_cards, pagination_status, selectedItems, selectedItemsIds):
    call_context = dash.callback_context.triggered[0]
    context = call_context['prop_id'].split('.')[0]
    if 'update_trigger' in call_context['prop_id'] and not update_trigger:
        raise PreventUpdate 
    
    if update_trigger: 
        selected = []
        for i, (n_clicks, id) in enumerate(zip(selectedItems, selectedItemsIds)):
            if n_clicks is not None and n_clicks % 2 != 0: 
                selected.append(selectedItemsIds[i].get('index'))
        cards_df = crud_op_db.read_food_cards()
        if not cards_df.empty:
            pagination_status = {
                'first_id': min(cards_df['type_id_int']),
                'last_id': max(cards_df['type_id_int'])
            }
            return {
                    'metadata': {
                            'filter': False
                        },
                    'data': {
                        'cards_values': cards_df.to_dict('records'),
                        'selected': selected
                        }
                }, pagination_status #, ''
        else: 
            return {}, {} #, components.no_data_toast()

    if 'card_container' in call_context['prop_id']:
        context_dict = json.loads(call_context['prop_id'].split('.')[0])
        className = cardContainerClass[int(context_dict['index'].split('_')[1])]
        if className != 'destroy_card': 
            raise PreventUpdate
        else: 
            selected = []
            for i, (n_clicks, id) in enumerate(zip(selectedItems, selectedItemsIds)):
                if n_clicks is not None and n_clicks % 2 != 0: 
                    selected.append(selectedItemsIds[i].get('index'))
        
            cards_df = crud_op_db.read_food_cards()

            if not cards_df.empty:
                pagination_status = {
                    'first_id': min(cards_df['type_id_int']),
                    'last_id': max(cards_df['type_id_int'])
                }
                return {
                        'metadata': {
                                'filter': False
                            },
                        'data': {
                            'cards_values': cards_df.to_dict('records'),
                            'selected': selected
                            }
                    }, pagination_status #, ''
            else: 
                return {}, {} #, components.no_data_toast()

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
            }, pagination_status #, ''
        else: 
            raise PreventUpdate

    elif not 'url' in call_context['prop_id'] and call_context['value'] > 0: 
        if context == 'next': 
            # Get the next 10 cards
            cards_df = crud_op_db.read_food_cards(id_int=pagination_status['last_id'])
            if not cards_df.empty:
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
                        }}, pagination_status #, ''

        elif context == 'prev': 
            # get the previous 10 cards
            cards_df = crud_op_db.read_food_cards(
                id_int=pagination_status['first_id'], 
                next=False
            )
            if not cards_df.empty:
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
                        }}, pagination_status #, ''

        elif context == 'show_all': 
            cards_df = crud_op_db.read_food_cards(show_all=True)
            if not cards_df.empty:
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
                        }}, pagination_status #, ''
            
        raise PreventUpdate

    if pathname == '/items-selection' and current_user.is_authenticated:
        cards_df = crud_op_db.read_food_cards()
        
        if not cards_df.empty:
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
                    }}, pagination_status #, ''
        else: 
            return {}, {} #, components.no_data_toast()

    else:
        raise PreventUpdate


@app.callback(
    Output('show_cards', 'children'),
    Input('input_data', 'data')
)
def show_cards_page(input_data):
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
    Input({'id': 'card_body_value', 'index': ALL}, 'className'),
    Input({'id': 'card_body', 'index': ALL}, 'className'),
    Input('input_data', 'data')
)
def update_list_items(classNameValues, classNameBody, input_data):
    input_data = input_data or {'data': {}}

    current_cards = pd.DataFrame.from_dict(input_data['data'].get('cards_values', []))
    if current_cards.empty:
        raise PreventUpdate

    previous_selected = hlp.update_and_aggr(current_cards)
    new_list = hlp.foods_listing(previous_selected)
    return show_items(new_list, True)


# Enable card elements if "Start" button clicked ! 
@app.callback(
    Output({'id': 'card_body', 'index': MATCH}, 'className'),
    Output({'id': 'commit_substraction_btn', 'index': MATCH}, 'children'), 
    Output({'id': 'commit_substraction_btn', 'index': MATCH}, 'color'), 
    Output({'id': 'commit_substraction_btn', 'index': MATCH}, 'disabled'),
    Input({'id': 'commit_substraction_btn', 'index': MATCH}, 'n_clicks'),
    State({'id': 'commit_substraction_btn', 'index': MATCH}, 'children'), 
    prevent_initial_call=True
)
def enable_card(subBtn, subBtnState): 
    if subBtnState == 'Start': 
        callContext = dash.callback_context.triggered[0]
        context = json.loads(callContext['prop_id'].split('.')[0])
        re_order = crud_op_db.on_production(int(context['index'].split('_')[0]))
        if re_order:
            return 'enable_card re_order', 'Stop', 'danger', False
        else: 
            return 'enable_card', 'Stop', 'danger', False
    raise PreventUpdate

# Destroy/hide the card if "Stop" button clicked !
@app.callback(
    Output({'id': 'card_container', 'index': MATCH}, 'className'),
    Output({'id': 'popover', 'index': MATCH}, 'is_open'),
    Input({'id': 'commit_substraction_btn', 'index': MATCH}, 'n_clicks'), 
    State({'id': 'commit_substraction_btn', 'index': MATCH}, 'children'), 
    State('input_data', 'data'), 
    State({'id': 'popover', 'index': MATCH}, 'is_open'),
    prevent_initial_call=False
)   
def destroy_card(subBtn, subBtnState, input_data, is_open):  
    
    if subBtnState == 'Stop' and dash.callback_context.triggered[0]['value']: 
        context = json.loads(
            dash.callback_context.triggered[0].get('prop_id', None).split('.')[0]
        )
        # Commit the card subtraction to our database: 
        type_id_int = int(context['index'].split('_')[0])
        selected_items = crud_op_db.get_selected_items(type_id_int)
        input_data = pd.DataFrame.from_dict(input_data['data']['cards_values'])
        card_food = input_data[input_data['type_id_int'] == type_id_int] 
        if len(card_food) == len(selected_items):
            crud_op_db.delete_selected_items(selected_items)
            crud_op_db.out_production(type_id_int)
            crud_op_db.update_vals(card_food)
            return 'destroy_card', False
        else: 
            return '', True
    raise PreventUpdate

# Show gang items
@app.callback(
    Output({'id': 'gang_items', 'index': MATCH}, 'className'), 
    Output({'id': 'show_gang_items', 'index': MATCH}, 'children'),
    Input({'id': 'show_gang_items', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)
def show_gang_items(gangBtn): 
    if gangBtn%2 == 0:
        expand = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                                    <i class="fa fa-expand fa-2x" aria-hidden="true"></i>               
                                ''')
        return 'hide', expand
    compress = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                    <i class="fa fa-compress fa-2x" aria-hidden="true"></i>               
                ''')
    return '', compress


# Show card Bonus
@app.callback(
    Output({'id': 'bonus_section_card', 'index': MATCH}, 'className'),
    Output({'id': 'bonus_btn_card', 'index': MATCH}, 'children'),
    Input({'id': 'bonus_btn_card', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
) 
def show_card_bonus(bonusBtn):
    if bonusBtn%2 == 0:
        bonusBtnIcon = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                        <i class="fa fa-chevron-circle-down fa-2x" aria-hidden="true"></i>               
                    ''')
        return 'hide-bonus', bonusBtnIcon
    bonusBtnIcon = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                    <i class="fa fa-minus-circle fa-2x" aria-hidden="true"></i>               
                ''')
    return 'show-bonus', bonusBtnIcon


# Handle cardElements clicks
@app.callback(
    Output({'id': 'card_body_value', 'index': MATCH}, 'className'),
    Input({'id': 'card_body_value', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
) 
def select_item(cardItem): 
    callContext = dash.callback_context.triggered[0]
    if cardItem is None or callContext.get('value', 0) == 0:
        raise PreventUpdate 
    context = json.loads(callContext['prop_id'].split('.')[0])
    if cardItem%2==0: 
        # Delete selected items from tmp table
        crud_op_db.delete_selected_item(context)
        return 'card-item'

    # Insert all gang items into tmp table
    crud_op_db.insert_selected_item(context)
    return 'card-item crossout-item'


# Handle cardElements clicks (If Gang-x clicked)
@app.callback(
    Output({'id': 'card_body_value_gang', 'index': MATCH}, 'className'),
    Input({'id': 'card_body_value_gang', 'index': MATCH}, 'n_clicks'), 
    State({'id': 'card_body_value_gang', 'index': MATCH}, 'className'),
    prevent_initial_call=True
) 
def select_item(cardItem, cardItemClass): 
    if cardItem is None:
        raise PreventUpdate 

    if cardItem%2==0: 
        return 'card-item'
    return 'card-item crossout-item'


@app.callback(
    Output({'id': 'card_body_value', 'index': ALL}, 'n_clicks'),
    Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'),
    Input({'id': 'card_body_value_gang', 'index': ALL}, 'n_clicks'),
    State({'id': 'card_body_value', 'index': ALL}, 'id'),
    State({'id': 'card_body_value', 'index': ALL}, 'className'),
    State({'id': 'card_body_value', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_card_item(currentListItem, gangClicks, cardBodyIds, itemClassName, cardBodyVal): 
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if 'card_body_value_gang' in context: 
        value = dash.callback_context.triggered[0].get('value', None)
        context_dict = json.loads(context)
        gang_items = context_dict['index'].split()
        idx = [i for i, d in enumerate(cardBodyIds) if f"{context_dict['index']}_" in d['index']]
        if value%2 == 0:
            for i in idx: 
                cardBodyVal[i] = 2
        else: 
            for i in idx: 
                cardBodyVal[i] = 1

        return cardBodyVal
    
    if 'lst_item_btn' in context and dash.callback_context.triggered[0]['value'] is not None:
        context_dict = json.loads(context)
        type_id_str = context_dict['index']
        for idx, (itemId, classNm) in enumerate(zip(cardBodyIds, itemClassName)):
            if str(type_id_str) in itemId['index'] and 'crossout-item' not in classNm:
                cardBodyVal[idx] = 1
                return cardBodyVal

    raise PreventUpdate


@app.callback(
    Output({'id': 'bonus_section', 'index': MATCH}, 'className'), 
    Output({'id': 'bonus_btn', 'index': MATCH}, 'children'), 
    Input({'id': 'bonus_btn', 'index': MATCH}, 'n_clicks'), 
    prevent_initial_call=True
)
def show_bonus(bonus_btn): 
    if bonus_btn%2 == 0:
        bonus_icon = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                        <i class="fa fa-chevron-circle-down fa-2x" aria-hidden="true"></i>               
                    ''')
        return 'hide-bonus', bonus_icon
    bonus_icon = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                    <i class="fa fa-minus-circle fa-2x" aria-hidden="true"></i>               
                ''')
    return 'show-bonus', bonus_icon


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
        if data is not None:
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
