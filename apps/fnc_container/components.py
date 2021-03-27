import dash_bootstrap_components as dbc
import dash_html_components as html
from app import  app
import plotly.express as px
from apps.fnc_container import helpers
import dash_core_components as dcc

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
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
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
            vertical=False,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_HIDEN,
)

def build_a_link(test=False):
    if test: 
        btn_link = dbc.Row([
                html.Div(id= 'go_to_details', children=[
                        html.Div(
                            dcc.Link(
                                dbc.Button(
                                    "Show Details", outline=True, color="secondary", className="mr-1"
                                ),
                                href='/subtraction-details',
                                id='details_btn',
                        ))
                    ], style={'display': 'none'}),
                dbc.Button("Filter", outline=True, color="secondary", className="mr-1", id="btn_filter_modal"), 
            ], 
            no_gutters=True,
            className="ml-auto flex-nowrap mt-3 mt-md-0",
            align="center")
        return btn_link
    
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
    for i, card in df.drop_duplicates(subset=['type_id_int']).iterrows():    
        row.append(
            html.Div(
                html.Div([
                    html.H4(f'Tisch {card["card_index"]}', style={'marginBottom': '25px', 'textAlign': 'center'}),
                    html.Div([
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    id='page2_items',
                                    children=[
                                        dbc.ListGroup([
                                            dbc.ListGroupItem(
                                                children=helpers.get_tot_quantity(row), 
                                                style={'padding': '8px'}
                                            )
                                            for j, row in df.loc[df['type_id_int'] == card['type_id_int']].iterrows()

                                        ])
                                    ]), width=3
                            ),
                            dbc.Col(
                                html.Div(dcc.Graph(figure=build_pie(
                                    df.loc[df['type_id_int'] == card['type_id_int']], 
                                    'quantity',
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
        if (i+1)%n_for_each_row==0: 
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


def get_filter_slidebar(): 
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
        style=SIDEBAR_HIDEN,
    )
    return sidebar



filter_modal = dbc.Modal(
            [
                dbc.ModalHeader("Sort Cards"),
                dbc.ModalBody(
                    html.Div(
                        children=[
                            html.P('Filter by specific date:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='date_picker_1',
                                    multi=True,
                                    options=[],
                                    placeholder='YYYY-MM-DD',
                                ), 
                                className='dcc_control'
                            ), 

                            html.P('Filter by specific time:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='datetime_picker_1',
                                    multi=True,
                                    options=[],
                                    placeholder='HH:MM:SS',
                                ), 
                                className='dcc_control'
                            ), 

                            html.P('Filter by table index:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='card_index_1',
                                    multi=True,
                                    options=[],
                                    placeholder='100 ...',
                                ), 
                                className='dcc_control'
                            ),

                            html.P('Filter by table Gang number:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='gang_number_1',
                                    multi=True,
                                    options=[],
                                    placeholder='1. Gang',
                                ), 
                                className='dcc_control'
                            ),

                            html.P('Filter by plate types:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='plate_type_1',
                                    multi=True,
                                    options=[],
                                    #placeholder='...',
                                    className='dcc_control'
                                )
                            ),

                            html.P('Filter by Phrase:', className='control_label'),
                            html.Div(
                                dcc.Dropdown(
                                    id='phrase_1',
                                    multi=True,
                                    options=[],
                                    #placeholder='...',
                                ), 
                                className='dcc_control'
                            ),

                            html.P('Sort by:', className='control_label'),
                            html.Div(
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Date", "value": 'card_date'},
                                        {"label": "Phrase", "value": 'card_phrase'},
                                        {"label": 'Card Number', 'value': 'card_index'}
                                    ],
                                    value='card_index',
                                    id="sort_by",
                                    inline=True,
                                    className='sort'
                                ),
                                className='dcc_control'
                            ),

                            html.P('How:', className='control_label'),
                            html.Div(
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Asc", "value": 1},
                                        {"label": "Desc", "value": 0},
                                    ],
                                    value=1,
                                    id="sort_how",
                                    inline=True,
                                    className='sort'
                                ),
                                className='dcc_control'
                            )
                        ]
                    ),
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Process", id="apply_filter", className="ml-auto"
                    )
                ),
            ],
            id="filter_modal",
            centered=True,
        )