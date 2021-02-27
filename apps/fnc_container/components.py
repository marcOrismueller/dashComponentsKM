import dash_bootstrap_components as dbc
import dash_html_components as html
from app import  app
import plotly.express as px
from apps.fnc_container import helpers
import dash_core_components as dcc

def build_a_link(): 
    btn_link = dbc.Row([
        dbc.Col(
            html.A(
                dbc.Button(
                    'Control Panel',
                    outline=True,
                    color="light",
                    className="mr-1", 
                    style={'border': '0px'}
                ), 
                href='/items-selection'
            ),
            width="auto"
        ),
        dbc.Col(
            html.A(
                dbc.Button(
                    'Data Board',
                    outline=True,
                    color="light",
                    className="mr-1", 
                    style={'border': '0px'}
                ), 
                href='/subtraction-details'
            ),
            width="auto"
        )],
        no_gutters=True,
        className="ml-auto flex-nowrap mt-3 mt-md-0",
        align="center"
    )
    return btn_link


def navbar(): 
    navbar = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url("logo.png"), height="50px", id='logo')),
                        #dbc.Col(dbc.NavbarBrand("SaCoSo KM", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/items-selection",
            ),
            dbc.Collapse(id="navbar-collapse", navbar=True), 
        ],
        color="dark",
        dark=True,
        style={'padding': '0.5% 2% 0.5% 3%'}
    )
    return navbar

def build_pie(df, values, names, color='type_only', height=350):
    fig = px.pie(
        df,
        values=values,
        names=names,
        color=color,
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(t=0,r=0,b=0,l=0),
        autosize=True,
        height=height,
        uniformtext_minsize=12, 
        uniformtext_mode='hide',
        title_x=0.5,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
    )
    return fig


def get_cards_details(df, n_for_each_row=2):
    result = []
    row = []
    for i, card_index in enumerate(df['card_index'].drop_duplicates(), start=1):           
        row.append(
            html.Div(
                html.Div([
                    html.H4(f'Tisch {card_index}', style={'marginBottom': '25px', 'textAlign': 'center'}),
                    html.Div([
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    id='page2_items',
                                    children=[
                                        dbc.ListGroup([
                                            dbc.ListGroupItem(
                                                children=[
                                                    f'{helpers.get_tot_quantity(row)}']
                                            )
                                            for j, row in df.loc[df['card_index'] == card_index].iterrows()

                                        ])
                                    ]), width=3
                            ),
                            dbc.Col(
                                html.Div(dcc.Graph(figure=build_pie(
                                    df.loc[df['card_index'] == card_index], 
                                    'total_quantity',
                                    'type_only', 
                                    'type_only', 
                                    250,
                                    ))
                                )
                            )
                        ], style={'alignItems': 'center'}),
                    ], style={'width': '96%'}),
                ], className='column'), 
                className='pretty_container', 
                style={'width': '48%'}
            )
        )
        if i%n_for_each_row==0: 
            result.append(
                html.Div(
                    row, 
                    className='row flex-display'
                )
            )
            row = []
    if row: 
        result.append(
                html.Div(
                    row, 
                    className='row flex-display'
                )
            )

    return result