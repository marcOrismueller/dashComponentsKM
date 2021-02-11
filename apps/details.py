import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def build_page_2(historical_subtraction): 

    historical_subtraction = historical_subtraction or {}
    
    if historical_subtraction:
        cards_subtr = pd.DataFrame.from_dict(
            historical_subtraction.get('cards_subtraction_details', [])
        )
        total_subt_df = cards_subtr.groupby('type_id_str').agg({
                'total_quantity': 'sum', 
                'type': 'last'
            })

        cards_subtr['card_id'] = 'Card - ' + (cards_subtr['type_id_int']+1).astype(str)

        page2 = dbc.Container([
            html.Div([
                html.Div(html.H4('Total Subtracted From Each Item'), style={'textAlign': 'center'}),
                dbc.Row([
                    dbc.Col(
                        html.Div(
                                    id = 'page2_items', 
                                    children=[
                                        dbc.ListGroup([
                                        dbc.ListGroupItem(
                                            #id={'id': 'lst_item', 'index': i},
                                            children=[f'{row["type"]}']
                                        )
                                        for i, row in total_subt_df.iterrows()

                                    ], style={'marginTop': '10px', 'marginLeft': '10px'})
                            ]), width=3
                        ),
                        dbc.Col(
                            html.Div(dcc.Graph(figure = px.pie(
                                                total_subt_df, 
                                                values='total_quantity', 
                                                names='type', 
                                                color='type',
                                        ))
                            )
                        )
                ], style={'alignItems': 'center'})
            ], style={'marginBottom': '120px'}),
            html.Div([
                html.Div(html.H4('Total Items Subtracted By Each Card'), style={'textAlign': 'center', 'marginBottom': '70px'}),
                html.Div([
                    dbc.Row([
                            dbc.Col([
                                html.H2(f'Card - {card+1}', style={'marginBottom': '30px', 'textAlign': 'center'}),
                                html.Div([
                                        dbc.ListGroup([
                                        dbc.ListGroupItem(
                                            children=[f'{row["type"]}']
                                        )
                                        for i, row in cards_subtr.loc[cards_subtr['type_id_int'] == card].iterrows()
                                    ], style={'marginTop': '10px'})
                                ])
                            ], width=3),

                            dbc.Col(
                                html.Div(dcc.Graph(figure = px.pie(
                                                    cards_subtr.loc[cards_subtr['type_id_int'] == card], 
                                                    values='total_quantity', 
                                                    color='type',
                                            ), style={'marginLeft': '10vh'})
                                )
                            )
                        ], style={'alignItems': 'center', 'marginLeft': '70px'})

                        # For each card create the components above
                        for card in cards_subtr['type_id_int'].drop_duplicates()
                    ])
                ]),
                
        ], style={'marginTop': '100px'})
        
        return page2
