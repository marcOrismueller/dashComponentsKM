import dash_core_components as dcc
from dash_core_components.Store import Store
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app, server, login_manager, User
from apps import load_data, cards_list, details, auth_login, auth_signup, config
from apps.fnc_container import components
from flask_login import current_user, logout_user

app.layout = html.Div([
    html.Div(id='logout'),
    dcc.Interval(id='get_files_interval', interval=1000, n_intervals=1),
    dcc.Store(id='test', data=False),
    dcc.Store(id='update_trigger', data=False),
    dcc.Store(id='filter_options'),
    dcc.Store(id='currentSelectedlistItem'),
    dcc.Store(id='pagination_status'),
    dcc.Store(id='food_tracer'),
    dcc.Store(id='filtred_cards_tmp'), 
    dcc.Store(id='input_data'), 
    dcc.Store(id='historical_sales'),
    dcc.Store(id='filter_result'),
    dcc.Location(id='url', refresh=True),
    components.navbar(current_user),
    html.Div(
        id='page-content', 
    )
], style = {'marginBottom': '150px'})


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Update the index
@app.callback(
    Output('page-content', 'children'),
    Output('navbar-collapse', 'children'),
    Input('url', 'pathname'), 
)
def display_page(pathname):
    if pathname == '/login':
        return auth_login.layout, components.build_a_link(pathname, current_user)
    
    elif pathname == '/logout': 
        if current_user.is_authenticated:
            logout_user()
        return auth_login.layout, components.build_a_link(pathname, current_user)
    
    elif pathname == '/signup': 
        return auth_signup.layout, components.build_a_link(pathname, current_user)
    
    elif pathname == '/load-data': 
        if not current_user.is_authenticated: 
            return auth_login.layout, components.build_a_link(pathname, current_user)
        return load_data.layout, components.build_a_link(pathname, current_user)
    
    elif pathname == '/items-selection' or  pathname == '/':
        if not current_user.is_authenticated: 
            return auth_login.layout, components.build_a_link(pathname, current_user)
        return cards_list.layout, components.build_a_link(pathname, current_user)
    
    elif pathname == '/subtraction-details':
        if not current_user.is_authenticated: 
            return auth_login.layout, components.build_a_link(pathname, current_user)
        return details.layout, components.build_a_link(pathname, current_user)
    
    elif pathname == '/config':
        if not current_user.is_authenticated: 
            return auth_login.layout, components.build_a_link(pathname, current_user)
        return config.layout, components.build_a_link(pathname, current_user)
    
    else:
        return html.H3('404 "URL not found"'), components.build_a_link(pathname, current_user)
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=False)