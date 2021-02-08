from threading import Condition
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State, ALL
import json
import dash
from dash.exceptions import PreventUpdate
import json
from app import app


list_1 = ['5 Red', '4 Green 6 Yellow', '3 Blue 2 DarkRed', '9 Indigo 3 Red', '18 DarkRed', '12 DarkKhaki', '5 Pink', '5 Blue']
list_2 = ['10 Red 7 Yellow', '8 Blue', '4 Green', '5 Pink 10 Indigo', '20 DarkRed', '12 DarkKhaki']

def show_items(list_2=list_2, mainCallBack=True):
    if mainCallBack:
        return [
            dbc.ListGroupItem(
                id={'id': 'lst_item', 'index': i},
                children=[x]
            )
            for i, x in enumerate(list_2)
        ]
    
    return dbc.ListGroup([

        dbc.ListGroupItem(
            id={'id': 'lst_item', 'index': i},
            children=[x]
        )
        for i, x in enumerate(list_2)

    ], style={'marginTop': '10px', 'marginLeft': '10px'})


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def create_checkbox_opt(b):
    options = []
    if len(b.strip().split()) > 2:
        new_list = divide_chunks(b.strip().split(), 2)
        for x, item in enumerate(new_list):
            options.append(
                {"label": f'{" ".join(item)}', "value": x} #, "disabled": True
            )
        return options
    options.append({"label": b, "value": 0}) #, "disabled": True
    return options


def show_cards(list_1=list_1):

    cards = html.Div([
        dbc.Card(id={
                    'id': 'card',
                    'index': i
            }, children=[
            dbc.CardHeader(f"Card {i+1}"),
            dbc.CardBody(
                children=[
                    dbc.Checklist(
                        id={
                            'id': 'card_value',
                            'index': i
                        },
                        options=create_checkbox_opt(b),
                        value=[],  # list(range(len(create_checkbox_opt(b)))),
                        labelCheckedStyle={
                            #"color": "red", 
                            "textDecoration": 'line-through',
                            #"fontSize": "16px", 
                            #"transition": "line-through 1s"
                            },
                        className='card_value',
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
                        'index': i
                    },
                    disabled=True
                )],
                style={'textAlign': 'center'})
        ], style={'marginTop': '10px', 'marginRight': '10px', 'whiteSpace': 'pre-line'})

        for i, b in enumerate(list_1)
    ])

    return cards


layout = html.Div(
        id='page1', 
        children = [
            dbc.Row([
                dbc.Col( 
                    children=[
                        html.Content(
                            id='items', 
                            children=[
                                dbc.ListGroup(id='show_list', style={'marginTop': '10px', 'marginLeft': '10px'})
                            ]
                        )#, children=show_items())
                    ], 
                    width=3
                ),

                dbc.Col([
                    dbc.Container([
                        dbc.CardColumns(id='show_cards')#children=show_cards())
                    ], style={'marginRight': '15px'})
                ])
            ]),
            dbc.Row(id= 'pie_page', children=[
                dbc.Col(
                    dcc.Link(
                        dbc.Button(
                            "Show Details", outline=True, color="secondary", className="mr-1"
                        ),
                        href='/pie', 
                        style={'float': 'right', 'margin': '40px 30px 0 0'}, 
                        id='pie_page_btn', 
                ))
            ], style={'display': 'none'}),
            html.H3(id='test_output')
        ])


@app.callback(
    Output('show_list', 'children'),
    Output('show_cards', 'children'),
    Output('initial_data', 'data'),
    Input('input_data', 'data'), 
    State('latest_update', 'data')
)
def show_page(input_data, latest_update):
    if latest_update:
        listgroup_values = input_data['latest'].get('listgroup_values', [])
        cards_values = input_data['latest'].get('cards_values', [])
        
        return show_items(listgroup_values, True), show_cards(cards_values), {
            'listgroup_values': listgroup_values,
            'cards_values': cards_values
        }
        
    if not input_data:
        listgroup_values = list_2
        cards_values = list_1
    else: 
        listgroup_values = input_data['initial'].get('listgroup_values', [])
        cards_values = input_data['initial'].get('cards_values', [])

    return show_items(listgroup_values, True), show_cards(cards_values), {
            'listgroup_values': listgroup_values,
            'cards_values': cards_values
        }

def initialize(current_listgroup):
    status_data = {
        'default': current_listgroup,
        'positions': {},
    }
    for i, lst in enumerate(current_listgroup):
        status_data['positions'][i] = {}
        for items in lst: 
            if len(items.strip().split()) > 2:
                l = divide_chunks(items.strip().split(), 2)
                for j, el in enumerate(l): 
                    status_data['positions'][i][f'{el[1]}'] = int(el[0])
            
            else:           
                status_data['positions'][i][f'{items.strip().split()[1]}'] = int(items.strip().split()[0])
    return status_data


def process(list_1=list_2):
    new_list = []
    for items in list_1:
        if len(items.split()) > 2:
           l = [' '.join(items.split()[i * 2:(i + 1) * 2]) for i in range((len(items.split()) + 2 - 1) // 2 )]  
        else: 
           l = [items]
        new_list.append(l)
    return new_list

def sub(new_list, test):    
    new_l = new_list
    for card_idx in test:
        for val_col in test[card_idx]: 
            for i, l in enumerate(new_list):
                if val_col.split()[1] in ' '.join(l):
                    for j, x in enumerate(l): 
                        if val_col.split()[1] == x.split()[1] and int(x.split()[0]) >= int(val_col.split()[0]):
                            new_x_val = int(x.split()[0]) - int(val_col.split()[0])
                            if not new_x_val: 
                                new_l[i].pop(j)
                                if not new_l[i]:
                                    new_l.pop(i)
                            else:
                                new_x = f'{new_x_val} {val_col.split()[1]}'
                                new_l[i][j] = new_x
                            break
                            
    #new = [[' '.join(l)] for l in new_l]
    new = [' '.join(l) for l in new_l]
    return new

@app.callback(
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
    Output('items', 'children'),

    Input({'id': 'card_value', 'index': ALL}, 'value'),
    State({'id': 'card_value', 'index': ALL}, 'options'),
    State('initial_data', 'data'),
    State('items_state', 'data')
)
def substruct_if_clicked(card_values, card_options, initial_data, items_state):
    if not initial_data: 
        raise PreventUpdate
    items_state = items_state or {}

    btns_visibility = []
    selected_vals = {}
    for i, opts in enumerate(card_values):
        if opts:
            selected_vals[i] = [card_options[i][opt_idx]['label'] for opt_idx in opts]
            btns_visibility.append(False)
        else: 
            btns_visibility.append(True)
        
    # [' '.join(l) for l in current_listgroup]
    current_listgroup = initial_data['listgroup_values']
    new_items = sub(process(current_listgroup), selected_vals)

    # Disable .... 


    return btns_visibility, show_items(new_items, False)



# @app.callback(
#     Output({'id': 'card_value', 'index': ALL}, 'options'),
#     Output({'id': 'card_value', 'index': ALL}, 'labelStyle'),
#     Input({'id': 'card_value', 'index': ALL}, 'value'),
#     State({'id': 'card_value', 'index': ALL}, 'options'),
#     State('items_state', 'data'),
# )
def check_check(card_value, checklist_options, items_state):
    if not items_state: 
        raise PreventUpdate

    #if items_state:
    current_values = items_state['metadata']['results']
    # sub then check
    subs_values = [labels.get('label') for i, labels in enumerate(checklist_options) if i in card_value]
    for i, (labels, values) in enumerate(zip(checklist_options, card_value)):
        if values: 
            for j in values:
                subs_values.append(labels[j].get('label'))
    for val in subs_values:
        card_value_color = val.split()[1]
        value = int(val.split()[0])
        current_values[card_value_color] -= value
        
    new_options = []
    card_text_style = [None for i in range(len(checklist_options))]
    for idx1, options in enumerate(checklist_options):
        opts_list = []
        opts_value = []
        for idx2, option in enumerate(options):
            color = option['label'].split()[1]
            value = option['label'].split()[0]
            stock = current_values.get(color, None)
            if stock and stock >= int(value):
                option['disabled'] = False
                opts_value.append(idx2)
            else:
                #option['disabled'] = True
                card_text_style[idx1] = {'textDecoration': 'line-through'}
            opts_list.append(option)
        new_options.append(opts_list)

    return new_options, card_text_style




def substract(lst_items, checkboxes_disabled, card_value=None, init=True, display_next_page={'display':'none'}, clicked_idx=None):
    
    if init:
        lst_items = [[item] for item in lst_items]
        cards = {}
        data = {}
        metadata = {'total': {}}
        for idx, lst in enumerate(lst_items):
            for item in lst:
                new_item = divide_chunks(item.strip().split(), 2)
                for n_i in new_item:
                    if idx not in data:
                        data[idx] = {
                            f'{n_i[1]}': int(n_i[0])
                        }
                    else:
                        data[idx][f'{n_i[1]}'] = int(n_i[0])
                    if n_i[1] not in metadata['total']:
                        metadata['total'][f'{n_i[1]}'] = int(n_i[0])
                    else:
                        metadata['total'][f'{n_i[1]}'] += int(n_i[0])

        metadata['results'] = metadata['total']
        lst_items = {'data': data, 'metadata': metadata, 'cards': cards or {}}
    # Disable/Enable our cards values depends on the left lists/items
    new_options = []
    new_opt_value = []
    card_text_style = [None for i in range(len(checkboxes_disabled))]
    for idx1, options in enumerate(checkboxes_disabled):
        opts_list = []
        opts_value = []
        for idx2, option in enumerate(options):
            color = option['label'].split()[1]
            value = option['label'].split()[0]
            stock = lst_items['metadata']['results'].get(color, None)
            if stock and stock >= int(value):
                option['disabled'] = False
                opts_value.append(idx2)
            else:
                option['disabled'] = True
                card_text_style[idx1] = {'textDecoration': 'line-through'}
            opts_list.append(option)
        new_options.append(opts_list)

        new_opt_value.append(opts_value)

    lst_items['state_components'] = {
        'checklist': {
            'options': new_options,
            'value': new_opt_value,
            'style': card_text_style
        }, 
        'pie_page': display_next_page,
        'clicked_idx': clicked_idx,
    }

    return lst_items


@app.callback(
    Output('items_state', 'data'),
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    State({'id': 'card_value', 'index': ALL}, 'value'),
    State({'id': 'card_value', 'index': ALL}, 'options'),
    #State({'id': 'card_value', 'index': ALL}, 'value'),
    State('items_state', 'data'),
    State('initial_data', 'data'),
)
def cards_handler(n_click, card_value, checklist_options, items_state, initial_data):
    if not initial_data: 
        raise PreventUpdate

    items_state = items_state or {}

    if [click for click in n_click if click]:
        callback = dash.callback_context.triggered[0]['prop_id'].split('.')
        #if callback[-1]:
        display_next_page = {}
        clicked_btn = callback[0]
        clicked_btn = json.loads(clicked_btn)
        # If you select atleast one elements from the card you clicked...
        if card_value[clicked_btn["index"]]:
            card_labels = checklist_options[clicked_btn["index"]]
            subs_values = [labels.get('label') for i, labels in enumerate(card_labels) if i in card_value[clicked_btn["index"]]]
            items_data = items_state['data']
            items_meta = items_state['metadata']
            cards_clicked = items_state['cards']
            for val in subs_values:
                for idx in items_data:
                    card_value_color = val.split()[1]
                    item_value = items_data[idx].get(card_value_color)
                    if item_value:
                        value = int(val.split()[0])
                        items_data[idx][card_value_color] = item_value - value
                        items_meta['results'][card_value_color] -= value
                        card_index = f'Card {clicked_btn["index"]+1}'
                        if card_index not in cards_clicked:
                            cards_clicked[card_index] = {
                                f'{card_value_color}': value
                            }
                        else: 
                            if card_value_color not in cards_clicked[card_index]:
                                cards_clicked[card_index][card_value_color] = value
                            else: 
                                cards_clicked[card_index][card_value_color] += value
                        break

            return substract(items_state, checklist_options, card_value, False, display_next_page, clicked_btn["index"])
        else: 
            raise PreventUpdate

    return substract(initial_data['listgroup_values'], checklist_options, init=True)


@app.callback(
    Output('pie_page', 'style'),
    Output({'id': 'card', 'index': ALL}, 'style'),
    Input('items_state', 'data'),
    State({'id': 'card', 'index': ALL}, 'style'),
    #State('items', 'children'),
)
def update_items(items_state, cards):#, items):
    items_state = items_state or {}
    if not items_state:
        raise PreventUpdate

    display_next_page = items_state['state_components'].get('pie_page')
    clicked_idx = items_state['state_components']['clicked_idx']
    if clicked_idx is not None:
        cards[clicked_idx]['pointer-events'] = 'none'
        cards[clicked_idx]['visibility'] = 'hidden'
        cards[clicked_idx]['opacity'] = '0'
        cards[clicked_idx]['transition']= 'visibility 8s, opacity 8s linear'
    if items_state:
        data = items_state['data']
        meta_result = items_state['metadata']['results']
        new_list2 = []
        for idx in data:
            colors = []
            for color in data[idx]:
                if data[idx][color] > 0 and meta_result[color] > 0:
                    colors.append(f'{data[idx][color]} {color}')
            if colors:
                new_list2.append(' '.join(colors))
        return display_next_page, cards   
    return display_next_page, cards