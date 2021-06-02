import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
from app import app
from dash.exceptions import PreventUpdate
import dash
import plotly.graph_objects as go
from apps.fnc_container import components, crud_op_db, helpers

layout = html.Div([
    dcc.Tabs(
        id='dashboard_tabs', 
        value='general', 
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
        dcc.Tab(
            label='General', 
            value='general', 
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[
            html.Div(id='mainContainer', children=[
                html.Div(children=[
                    components.dashboard_filter(),
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
                                dcc.Loading(html.Div(id='pie_total'))
                            )
                        ], style={'alignItems': 'center'})
                    ], className='pretty_container nine columns'),
                ], className='row flex-display'),

                # Details (section 2)
                html.Div([
                    html.Div(html.H4('Speisen pro Tisch'), style={
                            'textAlign': 'center', 'marginTop': '70px'}),
                    dcc.Loading(html.Div(id='for_each_card'))
                ]),

            ])
        ]),

        dcc.Tab(
            label='Historical sales', 
            value='historical', 
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[
            html.Div(id='mainContainer', children=[
                html.Div([
                        html.Div([
                            html.Div([
                                html.P('Select a timeframe ', className='control_label'),
                                html.Div(
                                    dcc.DatePickerRange(
                                        id='timeframe_picker',
                                        start_date='',
                                        end_date='',
                                        updatemode='singledate',
                                        display_format='YYYY-MM-DD',
                                        style={'margin': '15px'}
                                    ),
                                    className=''
                                ),
                                html.Div([
                                    dbc.Button('Apply timeframe', id='apply_timeframe'),
                                ])
                            ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'})
                        ], className='pretty_container four columns'),  
                        html.Div(html.H5('All information below is based on the timeframe you selected ... '), className='pretty_container seven columns')
                ], className='row flex-display'),
                html.Div(children=[
                    html.Div(children=[
                        html.Div(
                            html.H5('The total quantity of food sold per table'), 
                            style={'textAlign': 'center', 'marginBottom': '30px'}
                        ),
                        dcc.Loading(html.Div(id='food_qt_per_table'))
                    ], className='pretty_container four columns'),

                    html.Div(
                        dcc.Loading(html.Div(id='historical_per_table')), 
                        className='pretty_container seven columns'
                    ),

                ], className='row flex-display'),

                # Details (section 2)
                html.Div(
                    children=[
                        html.Div(id='historical_per_food_table', className='pretty_container six columns'),
                        html.Div([
                            html.Div(id='section_2'), 
                            html.Div(id='historical_table')
                        ], className='pretty_container five columns'), 
                    ], 
                    className='row flex-display'),

            ])
        ])
    ])
])

@app.callback(
    Output('historical_sales', 'data'),
    Output('timeframe_picker', 'start_date'),
    Output('timeframe_picker', 'end_date'),
    Input('dashboard_tabs', 'value'), 
    Input('apply_timeframe', 'n_clicks'),
    State('historical_sales', 'data'),
    State('timeframe_picker', 'start_date'),
    State('timeframe_picker', 'end_date'),
)
def update_historical_data(dashboard_tabs, apply_timeframe, historical_sales, start_date, end_date): # 
    context = dash.callback_context.triggered
    if dashboard_tabs=='general': 
        historical_sales = crud_op_db.historical()
        return historical_sales, '', ''
    
    historical_sales = pd.DataFrame.from_dict(historical_sales)
    if context[0]['prop_id'] == 'apply_timeframe.n_clicks':
        historical_sales = historical_sales.loc[
                (historical_sales['sales_created'] >= start_date) &
                (historical_sales['sales_created'] <= end_date)
            ]
        return historical_sales.to_dict('records'), start_date, end_date
    
    # Init start and end dates
    start_date = min(historical_sales['sales_created'])
    end_date = max(historical_sales['sales_created'])
    return historical_sales.to_dict('records'), start_date, end_date


@app.callback(
    Output('section_2', 'children'),
    Input('historical_sales', 'data')
)
def show_more_details(historical_sales): 
    if not historical_sales: 
        raise PreventUpdate

    historical_sales = pd.DataFrame.from_dict(historical_sales)
    top_n = helpers.groupdf(historical_sales)
    
    top_n_qt = top_n.nlargest(10, 'Total quantity')
    top_n_qt = top_n_qt.sort_values(by=['Total quantity'], ascending=True)
    
    top_by_qt = go.Figure((go.Bar(
        x=top_n_qt['Total quantity'],
        y=top_n_qt['Food'],
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(color='rgba(50, 171, 96, 1.0)', width=0.8),
        ),
        name='Top 10 Foods by sold quantity',
        orientation='h',
    )))
    top_by_qt.update_layout(
        paper_bgcolor="#F9F9F9",
        plot_bgcolor="#F9F9F9",
        margin=dict(t=0, r=0, b=70, l=0),
        autosize=True,
        height=250
    )
    
    top_n_price = top_n.nlargest(10, 'Total price')

    top_n_price['Total price'] = top_n_price['Total price'].astype(float)
    top_n_price = top_n_price.sort_values(by=['Total price'], ascending=True).reset_index(drop=True)

    top_by_price = go.Figure(go.Bar(
        x=top_n_price['Total price'],
        y=top_n_price['Food'],
        marker=dict(
            color='#6378a6',
            line=dict(color='#6378a6', width=0.8),
        ),
        name='Top 10 Foods by sold price',
        orientation='h',
    ))

    top_by_price.update_layout(
        paper_bgcolor="#F9F9F9",
        plot_bgcolor="#F9F9F9",
        margin=dict(t=0, r=0, b=70, l=0),
        autosize=True,
        height=250
    )
    top_n_food = html.Div([
        html.Div([
            html.Div(children=[
                html.Div(html.H5('Top 10 Foods by sold quantity'), style={'textAlign': 'center', 'marginBottom': '30px'}),
                dcc.Graph(figure=top_by_qt, config={'displayModeBar': False})]),
            html.Div(children=[
                html.Div(html.H5('Top 10 Foods by total price (Revenue)'), style={'textAlign': 'center', 'marginBottom': '30px'}),
                dcc.Graph(figure=top_by_price, config={'displayModeBar': False})])
        ], style={'display': 'flex', 'flexDirection': 'column'})
    ])
    return top_n_food


@app.callback(
    Output('listgroup_total', 'children'),
    Output('pie_total', 'children'),
    Output('for_each_card', 'children'),
    Input('apply_filter_2', 'n_clicks'),
    State('filter_result', 'data'), 
)
def display_graphs(apply_filter, filter_result):
    if not filter_result: 
        raise PreventUpdate

    cards_subtr = pd.DataFrame.from_dict(filter_result)

     # Total Graphs components
    total_subt_df = cards_subtr.groupby('type_id_str').agg({
        'available_quantity': 'sum',
        'price': 'sum',
        'type': 'last',
        'type_only': 'last',
        'bonus': 'last',
        'gang_number': 'last',
        'process': 'last',
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
                'available_quantity',
                'type_only',
                'type_only'
            ), 
            config={'displayModeBar': False}
        )
         
    # graphs for each card:
    cards_subtr_by_index = cards_subtr.groupby(['type_id_int', 'type_id_str']).agg({
        'available_quantity': 'sum',
        'price': 'sum',
        'type': 'last',
        'type_only': 'last',
        'bonus': 'last',
        'gang_number': 'last',
        'process': 'last'
    }).reset_index()

    pie_for_each_card = None
    if not cards_subtr_by_index.empty:
        pie_for_each_card = components.get_cards_details(cards_subtr_by_index)
    return listgroup_children_total, pie_total_fig, pie_for_each_card

@app.callback(
    Output('food_qt_per_table', 'children'), 
    Input('historical_sales', 'data')
)
def show_per_table(historical_sales):

    if historical_sales: 
        historical_sales = pd.DataFrame.from_dict(historical_sales)
        food_per_table_df = historical_sales.groupby(['table']).agg({
            'available_quantity': 'sum',
            'price': 'sum'
        }).reset_index()
        food_per_table_df = food_per_table_df.rename(columns={
            'available_quantity': 'Total quantity', 
            'table': 'Table', 
            'price': 'Total price'
        })

        food_per_table = dcc.Graph(
            figure= components.build_pie(
                food_per_table_df,
                'Total quantity',
                'Table',
                'Table', 
                250
            ), 
            id='qt_per_tab', 
            config={
                'displayModeBar': False
            }
        )
        return food_per_table
    else: 
        raise PreventUpdate

@app.callback(
    Output('historical_per_table', 'children'), 
    Output('historical_per_food_table', 'children'),
    Output('historical_table', 'children'),
    Input('qt_per_tab', 'clickData'),
    State('historical_sales', 'data')
)
def show_historical(hoverData, historical_sales):
    if not historical_sales: 
        raise PreventUpdate
    
    historical_sales = pd.DataFrame.from_dict(historical_sales)
    
    hourly_df_1 = helpers.hourly_converter(historical_sales, ['sales_created', 'table'])
    hourly_df_2 = helpers.hourly_converter(historical_sales, ['sales_created', 'table', 'type_id_str'], True)
    hourly_df_2 = hourly_df_2.sort_values(by=['type_id_str', 'Date']).reset_index(drop=True)
    if hoverData:
        
        table = hoverData['points'][0]['customdata']
        color_discrete_map = {'table': hoverData['points'][0].get('color')}
        if table: 
            target_table_1 = hourly_df_1.loc[hourly_df_1['Table']==table[0]]
            historical_per_table = [
                html.Div(
                    html.H5(f'Historical sales (Table - {table[0]})'), 
                    style={'textAlign': 'center', 'marginBottom': '30px'}
                ),
                dcc.Graph(
                    figure= components.line_chart(
                        target_table_1,
                        x="Date", 
                        y="Total quantity", 
                        color='Table',
                        color_discrete_map=color_discrete_map
                    ), 
                    id='histo_per_tab', 
                    config={
                        'displayModeBar': False
                    }
                )
            ]
            target_table_2 = hourly_df_2.loc[hourly_df_2['Table']==table[0]]
            foods_per_table = [
                html.Div(
                    html.H5(f'All historical sales for all foods sold in Table - {table[0]}'), 
                    style={'textAlign': 'center', 'marginBottom': '30px'}
                ),
                html.Div(dcc.Graph(
                    figure= components.line_chart(
                        target_table_2,
                        x="Date", 
                        y="Total quantity", 
                        color='Food'
                    ), 
                    id='histo_per_tab2', 
                    config={
                        'displayModeBar': False
                    }
                ))]
            target_table_2['Date'] = pd.to_datetime(target_table_2['Date']).dt.date
            food_per_table = [
                html.Div(
                    html.H5(f'Daily historical sales in all the tables (Table - {table[0]})'), 
                    style={'textAlign': 'center', 'marginBottom': '30px'}
                ),
                html.Div(dbc.Table.from_dataframe(target_table_2.filter(['Date', 'Price', 'Total quantity', 'Food', 'Bonus']), striped=True, bordered=True, hover=True))
            ]
            return historical_per_table, food_per_table, foods_per_table
    
    else: 
        historical_per_table = [
                html.Div(
                    html.H5(f'Historical sales (Table - ALL)'), 
                    style={'textAlign': 'center', 'marginBottom': '30px'}
                ),
                dcc.Graph(
                    figure= components.line_chart(
                        hourly_df_1,
                        x="Date", 
                        y="Total quantity", 
                        color='Table'
                    ), 
                    id='histo_per_tab', 
                    config={
                        'displayModeBar': False
                    }
                )
            ]
        foods_per_table = [
            html.Div(
                html.H5(f'All historical sales for all foods sold in Table - ALL'), 
                style={'textAlign': 'center', 'marginBottom': '30px'}
            ),
            html.Div(dcc.Graph(
                    figure= components.line_chart(
                        hourly_df_2,
                        x="Date", 
                        y="Total quantity", 
                        color='Food'
                    ), 
                    id='histo_per_tab2', 
                    config={
                        'displayModeBar': False
                    }
                ))]
        hourly_df_2['Date'] = pd.to_datetime(hourly_df_2['Date']).dt.date
        food_per_table = [
            html.Div(
                html.H5(f'Daily historical sales in the selected table (Table - ALL)'), 
                style={'textAlign': 'center', 'marginBottom': '30px'}
            ),
            html.Div(dbc.Table.from_dataframe(hourly_df_2.filter(['Date', 'Price', 'Total quantity', 'Food', 'Bonus']), striped=True, bordered=True, hover=True))
        ]
        return historical_per_table, food_per_table, foods_per_table


@app.callback(
    Output('filter_result', 'data'),
    # Update the options based on the selected values from the other filters.
    Output('date_picker', 'options'),
    Output('process', 'options'),
    Output('gang_number', 'options'),
    Output('plate_type', 'options'),
    Output('phrase', 'options'),
    Input('date_range_picker', 'start_date'),
    Input('date_range_picker', 'end_date'),
    Input('date_picker', 'value'),
    Input('process', 'value'),
    Input('gang_number', 'value'),
    Input('plate_type', 'value'),
    Input('phrase', 'value'),
    State('date_picker', 'options'),
    State('process', 'options'),
    State('gang_number', 'options'),
    State('plate_type', 'options'),
    State('phrase', 'options'),
    State('historical_sales', 'data'),
)
def update_result(
    start_date, end_date,
    selected_dates,
    selected_cards,
    selected_gang_number,
    selected_plates,
    selected_phrases,
    date_picker_options,
    process_options,
    gang_number_options,
    plate_type_options,
    phrase_options,
    historical_sales
):
    historical_sales = historical_sales or {}
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if not historical_sales:
        raise PreventUpdate

    cards_subtraction = pd.DataFrame.from_dict(historical_sales).sort_values(by='card_datetime').reset_index(drop=True)
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
        cards_subtr = cards_subtr.query('process in @selected_cards')

    if selected_gang_number:
        cards_subtr = cards_subtr.query('gang_number in @selected_gang_number')

    if selected_plates:
        cards_subtr = cards_subtr.query('type_id_str in @selected_plates')

    if selected_phrases:
        cards_subtr = cards_subtr.query('waitress in @selected_phrases')

    # date_picker: update options
    if context != 'date_picker':
        date_picker_options = [{'value': x, 'label': x}
                               for x in cards_subtr['card_date'].drop_duplicates()]
        if not selected_cards and not selected_plates and not selected_phrases and context != 'date_range_picker' and not selected_gang_number:
            date_picker_options = [{'value': x, 'label': x}
                                   for x in cards_subtraction['card_date'].drop_duplicates()]

    # type_id_int: update options
    if context != 'process':
        process_options = [{'value': x['process'], 'label': x['process']}
                           for i, x in cards_subtr.drop_duplicates(subset=['process']).iterrows()]
        if not selected_dates and not selected_plates and not selected_phrases and context != 'date_range_picker' and not selected_gang_number:
            process_options = [{'value': x['process'], 'label': x['process']}
                               for i, x in cards_subtraction.drop_duplicates(subset=['process']).iterrows()]

    # gang_number: update options
    if context != 'gang_number':
        gang_number_options = [{'value': x, 'label': x}
                               for x in cards_subtr['gang_number'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_phrases and context != 'date_range_picker' and not selected_plates:
            gang_number_options = [{'value': x, 'label': x}
                                   for x in cards_subtraction['gang_number'].drop_duplicates()]

    # plate_type: update options
    if context != 'plate_type':
        plate_type_options = [{'value': x['type_id_str'], 'label': x['type_only']}
                              for i, x in cards_subtr.drop_duplicates(subset=['type_id_str']).iterrows()]
        if not selected_cards and not selected_dates and not selected_phrases and context != 'date_range_picker' and not selected_gang_number:
            plate_type_options = [{'value': x['type_id_str'], 'label': x['type_only']}
                                  for i, x in cards_subtraction.drop_duplicates(subset=['type_id_str']).iterrows()]

    # phrase: update options
    if context != 'phrase':
        phrase_options = [{'value': x, 'label': x}
                          for x in cards_subtr['waitress'].drop_duplicates()]
        if not selected_cards and not selected_dates and not selected_plates and context != 'date_range_picker' and not selected_gang_number:
            phrase_options = [{'value': x, 'label': x}
                              for x in cards_subtraction['waitress'].drop_duplicates()]

    return cards_subtr.to_dict('records'), date_picker_options, process_options, gang_number_options, plate_type_options, phrase_options


@app.callback(
    Output('date_range_picker', 'start_date'),
    Output('date_range_picker', 'end_date'),
    Output('date_picker', 'value'),
    Output('process', 'value'),
    Output('plate_type', 'value'),
    Output('phrase', 'value'),
    Output('gang_number', 'value'),
    Input('reset_filters', 'n_clicks'),
    Input('historical_sales', 'data')
)
def reset_filters(reset_filters, historical_sales):
    if not historical_sales:
        raise PreventUpdate
    cards_subtr = pd.DataFrame.from_dict(historical_sales).sort_values(by='card_datetime').reset_index(drop=True)
    cards_subtr['card_datetime'] = pd.to_datetime(cards_subtr['card_datetime'])
    min_date_allowed = cards_subtr['card_datetime'].values[0]
    max_date_allowed = cards_subtr['card_datetime'].values[-1]
    return str(min_date_allowed), str(max_date_allowed), [], [], [], [], []
