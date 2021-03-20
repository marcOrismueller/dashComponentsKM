# @app.callback(
#     Output({'id': 'commit_substraction_btn', 'index': ALL}, 'disabled'),
#     Output('items', 'children'),
#     Output({'id': 'card_value', 'index': ALL}, 'options'),
#     Output('subtract_from_listGrp', 'data'),
#     Input({'id': 'card_value', 'index': ALL}, 'value'),
#     Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'),
#     State({'id': 'card_value', 'index': ALL}, 'options'),
#     State('input_data', 'data'),
#     State('subtract_from_listGrp', 'data')
# )
# def substruct_if_clicked(card_values, lst_item_btn, card_options, input_data, subtract_from_listGrp):
#     input_data = input_data or {}
#     if not input_data or not card_options:
#         raise PreventUpdate

#     subtract_from_listGrp = subtract_from_listGrp or {
#             'initial': input_data['initial']['listgroup_values'], 
#             'current': input_data['initial']['listgroup_values']
#         }

#     context = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])
#     context_value = dash.callback_context.triggered[0]['value']
#     if context['id']=='lst_item_btn' and not context_value:
#         raise PreventUpdate


#     btns_visibility = []
#     selected_vals = {}
#     for i, opts in enumerate(card_values):
#         if opts:
#             selected_vals[i] = [card_options[i][opt_idx]['label'] for opt_idx in opts]
#             if len(opts) == len(card_options[i]):
#                 btns_visibility.append(False)
#             else:
#                 btns_visibility.append(True)
#         else:
#             btns_visibility.append(True)

#     current_listgroup = subtract_from_listGrp['initial']
#     cards_values_all = input_data['initial']['cards_values']
    
    
#     new_items, new_card_options =  hlp.subtract_selected_v3(current_listgroup, cards_values_all, selected_vals, card_options, card_values, context)

#     if context['id'] == 'lst_item_btn':
#         subtract_from_listGrp['initial'] = new_items.to_dict('records')
    
#     return btns_visibility, show_items(new_items, False), new_card_options, subtract_from_listGrp


import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    children=[
        dbc.Button("Sidebar", outline=True, color="secondary", className="mr-1", id="btn_sidebar"),
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Brand",
    brand_href="#",
    color="dark",
    dark=True,
    fluid=True,
)


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 62.5,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#f8f9fa",
}

SIDEBAR_HIDEN = {
    "position": "fixed",
    "top": 62.5,
    "left": "-16rem",
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

content = html.Div(

    id="page-content",
    style=CONTENT_STYLE)

app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
    ],
)


@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return html.P("This is the content of page 1!")
    elif pathname == "/page-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True, port='8049')





















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
                            hlp.type_line_break(f"{x['quantity']} {x['type']}", btns=True),
                            className='listItemBtn',
                            id={'id': 'lst_item_btn', 'index': x['type_id_int']},
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
                            hlp.type_line_break(f"{x['quantity']} {x['type']}", btns=True),
                            className='listItemBtn',
                            id={'id': 'lst_item_btn', 'index': x['type_id_int']},
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
            components.filter_modal,
            #components.get_filter_slidebar(),
            html.Div(children=[
                #dbc.Button("Filter", outline=True, color="secondary", className="mr-1", id="btn_sidebar"), 
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
            ]),
        ])

@app.callback(
    Output('show_list', 'children'),
    Output('show_cards', 'children'),
    Input('input_data', 'data'),
    #Input('filtred_cards', 'data')
)
def show_page(input_data): #, filtred_cards
    context = dash.callback_context.triggered

    if not input_data: 
            raise PreventUpdate

    input_data = input_data or {}
    # if len(context) > 1:
    #     input_data = input_data or {}
    # context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    # context_value = dash.callback_context.triggered[0]['value']
    # if context == 'filtred_cards' and context_value: 
    #     input_data = filtred_cards

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
    #State('filtred_cards', 'data'),
)
def substruct_if_clicked(card_values, card_options, input_data): #, filtred_cards
    input_data = input_data or {}
    # if filtred_cards: 
    #     input_data = filtred_cards
    
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
    
    
    new_items, new_card_options =  hlp.subtract_selected_v3(current_listgroup, cards_values_all, selected_vals, card_options, card_values)

    return btns_visibility, show_items(new_items, False), new_card_options



@app.callback(
    Output({'id': 'card_value', 'index': ALL}, 'value'), 
    Input({'id': 'lst_item_btn', 'index': ALL}, 'n_clicks'), 
    State({'id': 'card_value', 'index': ALL}, 'value'), 
    State({'id': 'card_value', 'index': ALL}, 'options'),
    State('input_data', 'data'),
)
def substruct_if_list_clicked(lst_item_btn, card_values, card_options, input_data): 
    context = None
    try:
        context = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])
        context_value = dash.callback_context.triggered[0]['value']
        if context['id']=='lst_item_btn' and not context_value:
            raise PreventUpdate
    except: 
        raise PreventUpdate
    if context: 
        card_values = hlp.click_list_handler(card_values, card_options, context, input_data['initial']['listgroup_values'])
    
    return card_values


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

# @app.callback(
#     Output("filter_modal", "is_open"),
#     Output('filtred_cards', 'data'),
#     Input("btn_filter_modal", "n_clicks"), 
#     Input("apply_filter", "n_clicks"),
#     State("filter_modal", "is_open"),
#     State('filtred_cards_tmp', 'data')
# )
# def toggle_modal(n1, n2, is_open, filtred_cards_tmp):
#     context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
#     context_value = dash.callback_context.triggered[0]['value']

#     if context == 'btn_filter_modal' and context_value:
#         return not is_open, {}

#     if context == 'apply_filter' and context_value: 
#         return not is_open, filtred_cards_tmp
#     return is_open, {}

# @app.callback(
#     Output('filtred_cards_tmp', 'data'),
#     Output('date_picker_1', 'options'), 
#     Output('card_index_1', 'options'),  
#     Output('plate_type_1', 'options'), 
#     Output('phrase_1', 'options'), 
#     Input('date_picker_1', 'value'), 
#     Input('card_index_1', 'value'),
#     Input('plate_type_1', 'value'),
#     Input('phrase_1', 'value'),
#     State('date_picker_1', 'options'),
#     State('card_index_1', 'options'),
#     State('plate_type_1', 'options'),
#     State('phrase_1', 'options'),
#     State('input_data', 'data')
# )
# def update_result(
#         selected_dates, 
#         selected_cards, 
#         selected_plates, 
#         selected_phrases, 
#         date_picker_options, 
#         card_index_options, 
#         plate_type_options, 
#         phrase_options, 
#         input_data_1
#     ):
    
#     input_data_1 = input_data_1 or {}
#     context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

#     if not input_data_1:
#         raise PreventUpdate

#     if context == 'input_data_1': 
#         return input_data_1, date_picker_options, card_index_options, plate_type_options, phrase_options

#     cards_values = pd.DataFrame.from_dict(
#             input_data_1['initial'].get('cards_values')
#         )
#     cards_subtr = cards_values.copy()
#     #cards_subs_copy = cards_subtr.copy()

#     if selected_dates: 
#         cards_subtr = cards_subtr.query('card_date in @selected_dates')

#     if selected_cards: 
#         cards_subtr = cards_subtr.query('card_index in @selected_cards')

#     if selected_plates: 
#         cards_subtr = cards_subtr.query('type_id_str in @selected_plates')

#     if selected_phrases: 
#         cards_subtr = cards_subtr.query('card_phrase in @selected_phrases')

#     # date_picker: update options
#     if context != 'date_picker': 
#         date_picker_options = [{'value': x, 'label': x} for x in cards_subtr['card_date'].drop_duplicates()]
#         if not selected_cards and not selected_plates and not selected_phrases and context != 'date_range_picker': 
#             date_picker_options = [{'value': x, 'label': x} for x in cards_values['card_date'].drop_duplicates()]
    
#     # card_index: update options
#     if context != 'card_index':
#         card_index_options = [{'value': x, 'label': x} for x in cards_subtr['card_index'].drop_duplicates()]
#         if not selected_dates and not selected_plates and not selected_phrases and context != 'date_range_picker': 
#             card_index_options = [{'value': x, 'label': x} for x in cards_values['card_index'].drop_duplicates()]

#     # plate_type: update options
#     if context != 'plate_type':
#         plate_type_options = [{'value': x, 'label': x.replace('_', ' ').title()} for x in cards_subtr['type_id_str'].drop_duplicates()]
#         if not selected_cards and not selected_dates and not selected_phrases and context != 'date_range_picker':
#             plate_type_options = [{'value': x, 'label': x.replace('_', ' ').title()} for x in cards_values['type_id_str'].drop_duplicates()]

#     # phrase: update options
#     if context != 'phrase':
#         phrase_options = [{'value': x, 'label': x} for x in cards_subtr['card_phrase'].drop_duplicates()]
#         if not selected_cards and not selected_dates and not selected_plates and context != 'date_range_picker':
#             phrase_options = [{'value': x, 'label': x} for x in cards_values['card_phrase'].drop_duplicates()]

#     input_data_1['initial']['cards_values'] = cards_subtr.to_dict('records')

#     return input_data_1, date_picker_options, card_index_options, plate_type_options, phrase_options
        

# @app.callback(
#     Output('input_data', 'data'),
#     Input('input_data_1', 'data'),
#     Input('time_filter', 'value'),
#     Input('phrase_filter', 'value'),
#     Input('card_number_filter', 'value'),
#     State('input_data_1', 'data')
# )
def filter_sort_cards(input_data, time_filter, phrase_filter, card_number_filter, input_data_state):
    if not input_data_state: 
        raise PreventUpdate

    print('time_filter', time_filter)
    print('phrase_filter', phrase_filter)
    print('card_number_filter', card_number_filter)

    return input_data

