import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app
from apps import load_data, cards_list, details

server = app.server

app.layout = html.Div([
    dcc.Store(id='input_data', storage_type='session'),
    dcc.Store(id='historical_subtraction'),
    dcc.Location(id='url', refresh=False),
    html.Div(
        id='page-content', 
    )
], style = {'marginBottom': '150px'})

# Update the index
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'), 
    State('historical_subtraction', 'data'), 
)
def display_page(pathname, historical_subtraction):
    if pathname == '/':
        return load_data.layout
    elif pathname == '/items-selection':
        return cards_list.layout
    elif pathname == '/subtraction-details':
        return details.build_page_2(historical_subtraction)
    else:
        return dcc.H3('404 "URL not found"')
    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    app.run_server(debug=False)