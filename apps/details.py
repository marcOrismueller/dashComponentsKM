import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
from app import app
from dash.exceptions import PreventUpdate
import dash 
from apps.fnc_container import components, helpers


def build_page_2():
        # Details (section 1)
        page2 = html.Div([
            html.Div(id='mainContainer', children=[
                html.Div(children=[
                    html.Div(id='cross-filter-options', children=[
                        html.P('Filter by date range:', className='control_label'),
                        html.Div(
                                dcc.DatePickerRange(
                                    id='date_range_picker',
                                    start_date='',
                                    end_date='',
                                    updatemode='singledate', 
                                    display_format='YYYY-MM-DD'
                                ), 
                                className='dcc_control'
                        ),

                        html.P('Filter by specific date:', className='control_label'),
                        html.Div(
                            dcc.Dropdown(
                                id='date_picker',
                                multi=True,
                                options=[],
                                placeholder='YYYY-MM-DD',
                            ), 
                            className='dcc_control'
                        ),
                        
                        html.P('Filter by table index:', className='control_label'),
                        html.Div(
                            dcc.Dropdown(
                                id='card_index',
                                multi=True,
                                options=[],
                                placeholder='100 ...',
                            ), 
                            className='dcc_control'
                        ),

                        html.P('Filter by table Gang number:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='gang_number',
                                    multi=True,
                                    options=[],
                                    placeholder='1. Gang',
                                ), 
                                className='dcc_control'
                            ),

                        html.P('Filter by plate types:', className='control_label'),
                        html.Div(
                            dcc.Dropdown(
                                id='plate_type',
                                multi=True,
                                options=[],
                                #placeholder='...',
                                className='dcc_control'
                            )
                        ),

                        html.P('Filter by Phrase:', className='control_label'),
                        html.Div(
                            dcc.Dropdown(
                                id='phrase',
                                multi=True,
                                options=[],
                                #placeholder='...',
                            ), 
                            className='dcc_control'
                        ),

                        html.Div(
                            dbc.Button(
                                'reset', 
                                id='reset_filters', 
                                style={'float': 'right', 'marginRight': '5px'}
                                ), 
                                className='dcc_control'
                        )
                    ], className='pretty_container three columns'),

                    html.Div([
                        html.Div(html.H4('Gesamtübersicht aller Speisen'),
                                style={'textAlign': 'center'}),
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    id='page2_items',
                                    children=[
                                        dbc.ListGroup(
                                            id='listgroup_total', 
                                            style={'marginTop': '10px', 'marginLeft': '10px'})
                                    ]), width=3
                            ),
                            dbc.Col(
                                html.Div(id='pie_total')
                            )
                        ], style={'alignItems': 'center'})
                    ], className='pretty_container nine columns'),
                ], className='row flex-display'),

                # Details (section 2)
                html.Div([
                    html.Div(html.H4('Speisen pro Tisch'), style={'textAlign': 'center', 'marginTop': '70px'}),
                    dcc.Loading(html.Div(id='for_each_card'))
                ]),

            ]), 
            html.Div(id='test')
        ])
        return page2

@app.callback(
    Output('listgroup_total', 'children'),
    Output('pie_total', 'children'), 
    # Update the options based on the selected values from the other filters.
    Output('date_picker', 'options'), 
    Output('card_index', 'options'),  
    Output('gang_number', 'options'),
    Output('plate_type', 'options'), 
    Output('phrase', 'options'), 
    Output('for_each_card', 'children'),

    Input('date_range_picker', 'start_date'),
    Input('date_range_picker', 'end_date'), 
    Input('date_picker', 'value'), 
    Input('card_index', 'value'),
    Input('gang_number', 'value'),
    Input('plate_type', 'value'),
    Input('phrase', 'value'),
    State('date_picker', 'options'),
    State('card_index', 'options'),
    State('gang_number', 'options'),
    State('plate_type', 'options'),
    State('phrase', 'options'),
    State('historical_subtraction', 'data'),
)
def update_result(
        start_date, end_date, 
        selected_dates, 
        selected_cards, 
        selected_gang_number,
        selected_plates, 
        selected_phrases, 
        date_picker_options, 
        card_index_options, 
        gang_number_options,
        plate_type_options, 
        phrase_options, 
        historical_subtraction
    ):
    
    historical_subtraction = historical_subtraction or {}
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if not historical_subtraction:
        raise PreventUpdate

    cards_subtraction = pd.DataFrame.from_dict(
            historical_subtraction.get('cards_subtraction_details', [])
        ).sort_values(by='card_datetime').reset_index(drop=True)
    cards_subtr = cards_subtraction.copy()
    #cards_subs_copy = cards_subtr.copy()

    if start_date and end_date: 
        cards_subtr = cards_subtr.loc[
            (cards_subtr['card_date'] >= start_date.split('T')[0]) & 
            (cards_subtr['card_date'] <= end_date.split('T')[0])
        ]
    
    if selected_dates: 
        cards_subtr = cards_subtr.query('card_date in @selected_dates')

    if selected_cards: 
        cards_subtr = cards_subtr.query('card_index in @selected_cards')

    if selected_gang_number: 
        cards_subtr = cards_subtr.query('gang_number in @selected_gang_number')

    if selected_plates: 
        cards_subtr = cards_subtr.query('type_id_str in @selected_plates')

    if selected_phrases: 
        cards_subtr = cards_subtr.query('card_phrase in @selected_phrases')

    # date_picker: update options
    if context != 'date_picker': 
        date_picker_options = [{'value': x, 'label': x} for x in cards_subtr['card_date'].drop_duplicates()]
        if not selected_cards and not selected_plates and not selected_phrases and context != 'date_range_picker' and not selected_gang_number: 
            date_picker_options = [{'value': x, 'label': x} for x in cards_subtraction['card_date'].drop_duplicates()]
    
    # card_index: update options
    if context != 'card_index':
        card_index_options = [{'value': x, 'label': x} for x in cards_subtr['card_index'].drop_duplicates()]
        if not selected_dates and not selected_plates and not selected_phrases and context != 'date_range_picker'  and not selected_gang_number: 
            card_index_options = [{'value': x, 'label': x} for x in cards_subtraction['card_index'].drop_duplicates()]

    # gang_number: update options
    if context != 'gang_number':
        gang_number_options = [{'value': x, 'label': x} for x in cards_subtr['gang_number'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_phrases and context != 'date_range_picker' and not selected_plates:
            gang_number_options = [{'value': x, 'label': x} for x in cards_subtraction['gang_number'].drop_duplicates()]

    # plate_type: update options
    if context != 'plate_type':
        plate_type_options = [{'value': x['type_id_str'], 'label': x['type_only']} for i, x in cards_subtr.drop_duplicates(subset=['type_id_str']).iterrows()]
        if not selected_cards and not selected_dates and not selected_phrases and context != 'date_range_picker'  and not selected_gang_number:
            plate_type_options = [{'value': x['type_id_str'], 'label': x['type_only']} for i, x in cards_subtraction.drop_duplicates(subset=['type_id_str']).iterrows()]

    # phrase: update options
    if context != 'phrase':
        phrase_options = [{'value': x, 'label': x} for x in cards_subtr['card_phrase'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_plates and context != 'date_range_picker'  and not selected_gang_number:
            phrase_options = [{'value': x, 'label': x} for x in cards_subtraction['card_phrase'].drop_duplicates()]

    # Total Graphs components
    total_subt_df = cards_subtr.groupby('type_id_str').agg({
        'total_quantity': 'sum',
        'type': 'last', 
        'type_only': 'last', 
        'additionalInfo': 'last', 
        'gang_number': 'last',
    }).reset_index()
    
    listgroup_children_total = [
        dbc.ListGroupItem(
            children=helpers.get_tot_quantity(row), 
            style={'padding': '8px'}
        )
        for i, row in total_subt_df.iterrows()
    ]

    pie_total_fig = None
    if not total_subt_df.empty: 
        pie_total_fig = dcc.Graph(figure=components.build_pie(
                                        total_subt_df, 
                                        'total_quantity',
                                        'type_only', 
                                        'type_only'
                                    ))

    # graphs for each card:
    cards_subtr_by_index = cards_subtr.groupby(['card_index', 'type_id_str']).agg({
        'total_quantity': 'sum',
        'type': 'last',
        'type_only': 'last', 
        'additionalInfo': 'last',
        'gang_number': 'last',
    }).reset_index()

    pies_for_each_card = None
    if not cards_subtr_by_index.empty: 
        pies_for_each_card = components.get_cards_details(cards_subtr_by_index)

    return listgroup_children_total, pie_total_fig, date_picker_options, card_index_options, gang_number_options, plate_type_options, phrase_options, pies_for_each_card
        

@app.callback(
    Output('date_range_picker', 'start_date'),
    Output('date_range_picker', 'end_date'), 
    Output('date_picker', 'value'), 
    Output('card_index', 'value'),  
    Output('plate_type', 'value'), 
    Output('phrase', 'value'), 
    Output('gang_number', 'value'), 
    Input('reset_filters', 'n_clicks'),
    State('historical_subtraction', 'data')
)
def reset_filters(reset_filters, historical_subtraction): 
    if not historical_subtraction: 
        raise PreventUpdate
    cards_subtr = pd.DataFrame.from_dict(
            historical_subtraction.get('cards_subtraction_details', [])
        ).sort_values(by='card_datetime').reset_index(drop=True)
    cards_subtr['card_datetime'] = pd.to_datetime(cards_subtr['card_datetime'])       
    min_date_allowed = cards_subtr['card_datetime'].values[0]
    max_date_allowed = cards_subtr['card_datetime'].values[-1]

    return str(min_date_allowed), str(max_date_allowed), [], [], [], [], []



