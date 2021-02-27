import dash
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, external_stylesheets, dbc.themes.GRID], 
    title='SaCoSo KM',
    update_title=None,
)

#app.config['suppress_callback_exceptions'] = True

server = app.server

