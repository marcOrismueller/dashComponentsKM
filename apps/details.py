import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
#from app import app
import pandas as pd
import plotly.express as px

def build_page_2(items_state): 
    items_state = items_state or {}
    if items_state.get('data'):
        metadata = items_state['metadata']
        cards = items_state['cards']
        df_meta = pd.DataFrame()
        for initial, result in zip(metadata['total'], metadata['results']):
            df_meta = df_meta.append({
                'color': initial, 
                'value': int(metadata['total'][initial] - metadata['results'][result])
            }, ignore_index=True)
        
        df_cards = {}
        for card in cards:
            tmp = pd.DataFrame()
            for elem in cards[card]:
                tmp = tmp.append({
                    'color': elem, 
                    'value': int(cards[card][elem])
                }, ignore_index=True)
            tmp['card_index'] = card
            df_cards[card] = tmp

        page2 = dbc.Container([
            html.Div([
                html.Div(html.H4('Total Items Subtracted'), style={'textAlign': 'center'}),
                dbc.Row([
                    dbc.Col(
                        html.Div(
                                    id = 'page2_items', 
                                    children=[
                                        dbc.ListGroup([
                                        dbc.ListGroupItem(
                                            #id={'id': 'lst_item', 'index': i},
                                            children=[f'{int(row["value"])} {row["color"]}']
                                        )
                                        for i, row in df_meta.iterrows()

                                    ], style={'marginTop': '10px', 'marginLeft': '10px'})
                            ]), width=3
                        ),
                        dbc.Col(
                            html.Div(dcc.Graph(figure = px.pie(
                                                df_meta, 
                                                values='value', 
                                                names='color', 
                                                color='color',
                                                color_discrete_map= dict(zip(df_meta['color'], df_meta['color'])),
                                        ))
                            )
                        )
                ], style={'alignItems': 'center'})
            ], style={'marginBottom': '120px'}),
            html.Div([
                html.Div(html.H4('Total Items Subtracted By Each Card'), style={'textAlign': 'center'}),
                html.Div([
                    dbc.Row([
                            dbc.Col([
                                html.H2(card, style={'marginBottom': '30px', 'textAlign': 'center'}),
                                html.Div([
                                        dbc.ListGroup([
                                        dbc.ListGroupItem(
                                            children=[f'{int(row["value"])} {row["color"]}']
                                        )
                                        for i, row in df_cards[card].iterrows()
                                    ], style={'marginTop': '10px', 'marginLeft': '10px'})
                                ])
                            ], width=3),

                            dbc.Col(
                                html.Div(dcc.Graph(figure = px.pie(
                                                    df_cards[card], 
                                                    values='value', 
                                                    names='color', 
                                                    color='color',
                                                    color_discrete_map= dict(zip(df_cards[card]['color'], df_cards[card]['color'])),
                                            ), style={ "width" : "70vh", 'marginLeft': '10vh'})
                                )
                            )
                        ], style={'alignItems': 'center', 'marginLeft': '100px'})

                        # For each card create the components above
                        for card in df_cards
                    ])
                ]),
                
        ], style={'marginTop': '100px'})
        return page2
