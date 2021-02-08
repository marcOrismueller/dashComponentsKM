import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input, State, ALL
import json
import dash
from dash.exceptions import PreventUpdate
import json
from app import app
from apps.fnc_container import helpers as hlp

list_1 = ['5 Red', '4 Green 6 Yellow', '3 Blue 2 DarkRed', '9 Indigo 3 Red', '18 DarkRed', '12 DarkKhaki', '5 Pink', '8 Red', '4 Red']
list_2 = ['10 Red 7 Yellow', '8 Blue', '4 Green', '5 Pink 10 Indigo', '20 DarkRed', '12 DarkKhaki', '1 Red']

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
                        options=hlp.create_checkbox_opt(b),
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
                        )
                    ], 
                    width=3
                ),

                dbc.Col([
                    dbc.Container([
                        dbc.CardColumns(id='show_cards')
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
    #State('latest_update', 'data')
)
def show_page(input_data): 

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
    
@app.callback(
    Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
    Output('items', 'children'),
    Output({'id': 'card_value', 'index': ALL}, 'options'),

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
            if len(opts) == len(card_options[i]):
                btns_visibility.append(False)
            else: 
                btns_visibility.append(True)
        else: 
            btns_visibility.append(True)
        

    current_listgroup = initial_data['listgroup_values']
    new_items, new_card_options = hlp.subtract_selected(hlp.re_struct(current_listgroup), selected_vals, card_options, card_values)

    return btns_visibility, show_items(new_items, False), new_card_options


@app.callback(
    Output('items_state', 'data'),
    Input({'id': 'commit_substraction_btn', 'index': ALL}, 'n_clicks'),
    State({'id': 'card_value', 'index': ALL}, 'value'),
    State({'id': 'card_value', 'index': ALL}, 'options'),
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

            return hlp.commit_substraction(items_state, checklist_options, card_value, False, display_next_page, clicked_btn["index"])
        else: 
            raise PreventUpdate

    return hlp.commit_substraction(initial_data['listgroup_values'], checklist_options, init=True)


@app.callback(
    Output('pie_page', 'style'),
    Output({'id': 'card', 'index': ALL}, 'style'),
    Input('items_state', 'data'),
    State({'id': 'card', 'index': ALL}, 'style'),
)
def update_items(items_state, cards):
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