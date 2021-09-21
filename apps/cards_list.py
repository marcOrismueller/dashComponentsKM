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


def show_cards(cards_values_df, previous_selected):
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
    previousEnabledCards = [int(id.split('_')[0]) for id in previous_selected]
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
                                            cards_values_df.loc[(cards_values_df['type_id_int'] == card_id)], 
                                            previous_selected
                                        )
                                    )
                                ])
                            ],
                            className = 'enable_card' if card_id in previousEnabledCards else 'disabled' 
                        ),

                        dbc.CardFooter([
                            dbc.Button(
                                'Stop' if card_id in previousEnabledCards else 'Start',
                                color='danger' if card_id in previousEnabledCards else 'success',
                                size="lg",
                                className='m-4',
                                id={
                                    'id': 'commit_substraction_btn',
                                    'index': f'{int(card_id)}_{i}_{"_".join(list(cards_values_df[cards_values_df["type_id_int"]==card_id]["type_id_str"]))}'
                                },
                                disabled=False
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
        for i, card_id in enumerate(cards_values_df['type_id_int'].drop_duplicates())
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
)
def update_timer(n_intervals):
    mins, secs = divmod(30-(n_intervals%30), 60)
    timer = '{:02d}:{:02d}'.format(mins, secs)
    if 30-(n_intervals%30) == 30: 
        # Read the new files 
        res = read_files.update_data()
        return f'Checking for new files in {timer} (No data)', res
    return f'Checking for new files in {timer}', False
    

# Fetch data from our database
@app.callback(
    Output('input_data', 'data'),
    Output('pagination_status', 'data'),
    #Output('no_data', 'children'),
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
def show_page(input_data):
    context = dash.callback_context.triggered
    if context[0]['prop_id'] == '.':
        raise PreventUpdate
    if not input_data:
        raise PreventUpdate
    
    input_data = input_data or {}
    cards_values_df = pd.DataFrame.from_dict(input_data['data'].get('cards_values', []))
    previous_selected = input_data['data'].get('selected', [])
    return show_cards(cards_values_df, previous_selected)


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
        return 'enable_card', 'Stop', 'danger', False

    raise PreventUpdate

# Destroy/hide the card if "Stop" button clicked !
@app.callback(
    Output({'id': 'card_container', 'index': MATCH}, 'className'),
    Output({'id': 'popover', 'index': MATCH}, 'is_open'),
    Input({'id': 'commit_substraction_btn', 'index': MATCH}, 'n_clicks'), 
    State({'id': 'commit_substraction_btn', 'index': MATCH}, 'children'), 
    State('food_tracer', 'data'),
    State('input_data', 'data'), 
    State({'id': 'popover', 'index': MATCH}, 'is_open'),
    prevent_initial_call=False
)   
def destroy_card(subBtn, subBtnState, food_tracer, input_data, is_open):  #, selectedCardItems
    
    if subBtnState == 'Stop' and dash.callback_context.triggered[0]['value']: 
        context = json.loads(
            dash.callback_context.triggered[0].get('prop_id', None).split('.')[0]
        )
        # Commit the card subtraction to our database: 
        food_tracer = pd.DataFrame.from_dict(food_tracer)
        type_id_int = int(context['index'].split('_')[0])
        selected = food_tracer[food_tracer['type_id_int']==type_id_int]['selected'].tolist()
        if all(selected): 
            input_data = pd.DataFrame.from_dict(input_data['data']['cards_values'])
            card_food = input_data[input_data['type_id_int'] == type_id_int]
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
    if cardItem is None:
        raise PreventUpdate 

    if cardItem%2==0: 
        return 'card-item'
    return 'card-item crossout-item'


# Handle cardElements clicks (If Gang-x clicked)
# @app.callback(
#     Output({'id': 'card_body_value_gang', 'index': MATCH}, 'className'),
#     Input({'id': 'card_body_value_gang', 'index': MATCH}, 'n_clicks'), 
#     State({'id': 'card_body_value_gang', 'index': MATCH}, 'className'),
#     prevent_initial_call=True
# ) 
def select_item(cardItem, cardItemClass): 
    if cardItem is None:
        raise PreventUpdate 

    if cardItem%2==0: 
        return 'card-item'
    return 'card-item crossout-item'


# left list items controller
@app.callback(
    Output('show_list', 'children'),
    Output('food_tracer', 'data'),
    Output('currentSelectedlistItem', 'data'),
    Input('input_data', 'data'), 
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    Input({'id': 'card_body_value', 'index': ALL}, 'n_clicks'),
    Input({'id': 'card_body_value_gang', 'index': ALL}, 'n_clicks'),
    Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'),
    State({'id': 'commit_substraction_btn', 'index': ALL}, 'children'),
    State({'id': 'card_body_value', 'index': ALL}, 'className'),
    State('food_tracer', 'data')
)
def update_list_items(input_data, start_btn, card_body_value, gangClicks, lst_item_btn, start_btn_status, cardBodyValueClass,food_tracer): #
    input_data = input_data or {'data': {}}

    current_cards = pd.DataFrame.from_dict(input_data['data'].get('cards_values', []))
    if current_cards.empty:
        raise PreventUpdate

    food_tracer = food_tracer or crud_op_db.init_cards_tracer() 
    if not food_tracer: 
        raise PreventUpdate

    context = dash.callback_context.triggered
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
            new_cards, _ = hlp.intersection(current_cards, food_tracer)
            new_list = hlp.foods_listing(new_cards)
            return show_items(new_list, True), food_tracer.to_dict('records'), None
    
    if 'card_body_value' in cntxt and len(context) == 1: 
        food_tracer = hlp.item_selected(food_tracer, context)
        new_cards, _ = hlp.intersection(current_cards, food_tracer)
        new_list = hlp.foods_listing(new_cards)
        return show_items(new_list, True), food_tracer.to_dict('records'), None
    
    if  'lst_item_btn' in cntxt and len(context) == 1:
        new_cards, _ = hlp.intersection(current_cards, food_tracer)
        food_tracer = hlp.insert_selected_item_2(food_tracer, context, new_cards)
        new_cards, _ = hlp.intersection(current_cards, food_tracer)
        new_list = hlp.foods_listing(new_cards)
        context_dict = json.loads(cntxt.split('.')[0])
        return show_items(new_list, True), food_tracer.to_dict('records'), {'selectedItem': context_dict['index']}

    new_cards, food_tracer = hlp.intersection(current_cards, food_tracer, input_data['data'].get('selected', None))
    new_list = hlp.foods_listing(new_cards)

    return show_items(new_list, True), food_tracer.to_dict('records'), None


@app.callback(
    Output({'id': 'card_body_value', 'index': ALL}, 'n_clicks'),
    Input('currentSelectedlistItem', 'data'),
    Input({'id': 'card_body_value_gang', 'index': ALL}, 'n_clicks'),
    State('food_tracer', 'data'), 
    State({'id': 'card_body_value', 'index': ALL}, 'id'),
    State({'id': 'card_body_value', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_card_item(currentListItem, gangClicks, foodTracer, cardBodyIds, cardBodyVal): 
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if 'card_body_value_gang' in context: 
        value = dash.callback_context.triggered[0].get('value', None)
        context_dict = json.loads(context)
        gang_items = context_dict['index'].split()
        idx = [i for i, d in enumerate(cardBodyIds) if f"{context_dict['index']}_" in d['index']]
        if value%2 == 0:
            for i in idx: 
                cardBodyVal[i] = 0
        else: 
            for i in idx: 
                cardBodyVal[i] = 1
                
        return cardBodyVal
        
    if currentListItem: 
        foodTracer = pd.DataFrame.from_dict(foodTracer)
        if foodTracer.loc[foodTracer['type_id_str'] == currentListItem['selectedItem'], 'production'].iloc[0]:
            idx = next((index for (index, d) in enumerate(cardBodyIds) if currentListItem['selectedItem'] in d["index"]), None)
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
