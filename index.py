import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
from apps import load_data, cards_list, details
from apps.fnc_container import components

server = app.server


app.layout = html.Div([
    dcc.Store(id='filtred_cards'), 
    dcc.Store(id='filtred_cards_tmp'), 
    dcc.Store(id='input_data', storage_type='session'), 
    dcc.Store(id='historical_subtraction'),
    dcc.Store(id='substruct_items'),
    dcc.Store(id='gang_notifier'),
    dcc.Store(id='isFiltered'),
    dcc.Location(id='url', refresh=False),
    components.navbar(),
    html.Div(
        id='page-content', 
    )
], style = {'marginBottom': '150px'})

# Update the index
@app.callback(
    Output('page-content', 'children'),
    Output('navbar-collapse', 'children'),
    Input('url', 'pathname'), 
)
def display_page(pathname):
    if pathname == '/':
        return load_data.layout, ''
    elif pathname == '/items-selection':
        return cards_list.layout, components.build_a_link(True)
    elif pathname == '/subtraction-details':
        return details.build_page_2(), components.build_a_link()
    else:
        return html.H3('404 "URL not found"'), ''
    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    app.run_server(debug=False)