import dash_bootstrap_components as dbc
import dash_html_components as html
from app import app
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


def build_a_link(current_page, current_user):
    styleItems = {
        'display': 'block',
        'textDecoration': 'none',
        'color': 'black'
    }
    if current_user.is_authenticated:
        # make a reuseable dropdown for the different examples
        dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(
                    dcc.Link(
                        "Control Panel",
                        href='/items-selection',
                        style=styleItems
                    )
                ),
                dbc.DropdownMenuItem(
                    dcc.Link(
                        "Dashboard Details",
                        href='/subtraction-details',
                        style=styleItems,
                        id='go_to_details'
                    )
                ),
                dbc.DropdownMenuItem(
                    dcc.Link(
                        "Upload Data",
                        href='/load-data',
                        style=styleItems
                    )
                ),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem(
                    dcc.Link(
                        'Logout',
                        href='/logout',
                        style=styleItems,
                    )
                ),
            ],
            nav=True,
            in_navbar=True,
            label=f"Hi {current_user.user_fname.title()}!",
        )
        # make a reuseable navitem for the different examples
        nav_item = dbc.NavItem(
            dbc.Button("Filter", outline=True, color="secondary",
                       className="mr-1", id="btn_filter_modal", n_clicks=0),
            style={'marginRight': '30px'}
        )
        links = dbc.Nav([nav_item, dropdown], className="ml-auto", navbar=True)
    else:
        links = dbc.Nav(dcc.Link('Login', href='/login'),
                        className="ml-auto", navbar=True)
    # links=[]
    # if current_page == '/items-selection':
    #     links = [
    #             html.Div(id= 'go_to_details', children=[
    #                     html.Div(
    #                         dcc.Link(
    #                             dbc.Button(
    #                                 "Show Details", outline=True, color="secondary", className="mr-1"
    #                             ),
    #                             href='/subtraction-details',
    #                             id='details_btn',
    #                     ))
    #                 ], style={'display': 'none'}),
    #             dbc.Button("Filter", outline=True, color="secondary", className="mr-1", id="btn_filter_modal"),
    #         ]

    # elif '/subtraction-details':
    #     links = [
    #         dbc.Col(
    #             html.A(
    #                 dbc.Button(
    #                     'Control Panel',
    #                     outline=True,
    #                     color="light",
    #                     className="mr-1",
    #                     style={'border': '0px'}
    #                 ),
    #                 href='/items-selection'
    #             ),
    #             width="auto"
    #         ),
    #         dbc.Col(
    #             html.A(
    #                 dbc.Button(
    #                     'Data Board',
    #                     outline=True,
    #                     color="light",
    #                     className="mr-1",
    #                     style={'border': '0px'}
    #                 ),
    #                 href='/subtraction-details'
    #             ),
    #             width="auto"
    #         ),
    #     ]
    # else:

    # if current_user.is_authenticated:
    #     links.append(html.Div(
    #                 html.A('Logout', href='/logout'),
    #                 id="login_status"
    #             ))
    # else:
    #      links.append(html.Div(
    #                 html.A('Login', href='/login'),
    #                 id="login_status"
    #             ))
    # btn_link = dbc.Row(links,
    #     no_gutters=True,
    #     className="ml-auto flex-nowrap mt-3 mt-md-0",
    #     align="center"
    # )
    return links


def navbar(current_user):
    links = [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url(
                            "logo.png"), height="50px", id='logo')),
                    #dbc.Col(dbc.NavbarBrand("SaCoSo KM", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/items-selection",
        ),
        dbc.Collapse(id="navbar-collapse", navbar=True),
    ]

    navbar = dbc.Navbar(
        links,
        color="dark",
        dark=True,
        style={'padding': '0.5% 10% 0.5% 10%'}
    )
    return navbar


def build_pie(df, values, names, color='type_only', height=350):
    fig = px.pie(
        df,
        values=values,
        names=names,
        color=color,
        #hover_data=['Total price']
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(t=0, r=0, b=0, l=0),
        autosize=True,
        height=height,
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        title_x=0.5,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
    )
    return fig

def line_chart(df, x="Date", y="Total quantity", color='Table', color_discrete_map=None): 
    fig = px.line(df, x=x, y=y, color=color)
    fig.update_layout(
        margin=dict(t=0, r=0, b=20, l=0),
        autosize=True,
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        title_x=0.5,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        height=500, 
        template="plotly_white",
        
        xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
        )
    )
    return fig


def get_cards_details(df, n_for_each_row=2):
    result = []
    row = []
    for i, card in df.drop_duplicates(subset=['type_id_int']).iterrows():
        row.append(
            html.Div(
                html.Div([
                    html.H4(f'Tisch {card["process"]}', style={
                            'marginBottom': '25px', 'textAlign': 'center'}),
                    html.Div([
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    id='page2_items',
                                    children=[
                                        dbc.ListGroup([
                                            dbc.ListGroupItem(
                                                children=helpers.get_tot_quantity(
                                                    row),
                                                style={'padding': '8px'}
                                            )
                                            for j, row in df.loc[df['type_id_int'] == card['type_id_int']].iterrows()

                                        ])
                                    ]), width=3
                            ),
                            dbc.Col(
                                html.Div(dcc.Graph(figure=build_pie(
                                    df.loc[df['type_id_int'] ==
                                           card['type_id_int']],
                                    'available_quantity',
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
        if (i+1) % n_for_each_row == 0:
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
        dbc.ModalHeader("Filters"),
        dbc.ModalBody(
            html.Div(
                children=[
                    html.P('Specific date:',
                           className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='date_picker_1',
                            multi=True,
                            options=[],
                            placeholder='YYYY-MM-DD',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Specific time:',
                           className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='datetime_picker_1',
                            multi=True,
                            options=[],
                            placeholder='HH:MM:SS',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Table index:', className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='process_1',
                            multi=True,
                            options=[],
                            placeholder='100 ...',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Gang numbers:', className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='gang_number_1',
                            multi=True,
                            options=[],
                            placeholder='1. Gang',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Plate types:', className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='plate_type_1',
                            multi=True,
                            options=[],
                            # placeholder='...',
                            className='dcc_control'
                        )
                    ),

                    html.P('Phrases:', className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='phrase_1',
                            multi=True,
                            options=[],
                            # placeholder='...',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Sort by:', className='control_label'),
                    html.Div(
                        dbc.RadioItems(
                            options=[
                                {"label": "Date", "value": 'card_date'},
                                {"label": "Phrase", "value": 'waitress'},
                                {"label": 'Card Number', 'value': 'process'}
                            ],
                            value='process',
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
                "Process", id="apply_filter", className="ml-auto", n_clicks=0
            )
        ),
    ],
    id="filter_modal",
    centered=True,
)

def pagination(): 
    paginations = html.Div([
        html.Div(dbc.Button('Previous', id='prev', outline=True, n_clicks=0)), 
        html.Div(dbc.Button('Next', id='next', outline=True, n_clicks=0))
    ], className='row')

    return paginations

def no_data_toast(): 
    toast = html.Div(children=[
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4('No data available ..! please Updoad some foods data.'),
                        ], className='form-row', style={'marginTop': '30px'}),
                    ]),
                    html.Div([
                        html.A(dbc.Button('Upload Data', className='submit'), href='/load-data')
                    ])
                ], className='form-left')
            ], className='form-detail')
        ], className='form-v10-content', style={'maxWidth': '600px'})
    ], className='page-content')
    return toast

def dashboard_filter():
    filter = html.Div(id='cross-filter-options', children=[
                    html.P('Filter by date range:', className='control_label'),
                    dcc.Loading(html.Div(
                        dcc.DatePickerRange(
                            id='date_range_picker',
                            start_date='',
                            end_date='',
                            updatemode='singledate',
                            display_format='YYYY-MM-DD'
                        ),
                        className='dcc_control'
                    )),

                    html.P('Filter by specific date:',
                           className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='date_picker',
                            multi=True,
                            options=[],
                            placeholder='YYYY-MM-DD',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Filter by table index:',
                           className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='process',
                            multi=True,
                            options=[],
                            placeholder='100 ...',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Filter by table Gang number:',
                           className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='gang_number',
                            multi=True,
                            options=[],
                            placeholder='1. Gang',
                        ),
                        className='dcc_control'
                    ),

                    html.P('Filter by plate types:',
                           className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='plate_type',
                            multi=True,
                            options=[],
                            # placeholder='...',
                            className='dcc_control'
                        )
                    ),

                    html.P('Filter by Phrase:', className='control_label'),
                    html.Div(
                        dcc.Dropdown(
                            id='phrase',
                            multi=True,
                            options=[],
                            # placeholder='...',
                        ),
                        className='dcc_control'
                    ),

                    html.Div([
                        dbc.Button(
                            'reset',
                            id='reset_filters',
                            style={'float': 'right', 'marginRight': '5px'}, 
                            color='danger'
                        ),
                        dbc.Button(
                            'Apply & Show',
                            id='apply_filter_2',
                            style={'float': 'right', 'marginRight': '5px'}, 
                        )
                    ], className='dcc_control'), 
                ], className='pretty_container three columns')
    
    return filter