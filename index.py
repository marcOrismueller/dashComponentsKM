import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app
from apps import app0, app1, app2

server = app.server

app.layout = html.Div([
    dcc.Store(id='input_data'),
    dcc.Store(id='latest_update'),
    dcc.Store(id='test_store'),
    dcc.Store(id='initial_data'),
    dcc.Store(id='items_state'),
    dcc.Store(id='memory_tmp'),
    dcc.Location(id='url', refresh=False),
    html.Div(
        id='page-content', 
    )
], style = {'marginBottom': '150px'})

# Update the index
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'), 
    State('items_state', 'data'), 
)
def display_page(pathname, items_state):
    if pathname == '/pie':
        return app2.build_page_2(items_state)
    elif pathname == '/load-data':
        return app0.layout
    else:
        return app1.layout
    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    app.run_server(debug=False)