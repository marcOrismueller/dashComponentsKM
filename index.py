import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app, login_manager, User
from apps import load_data, cards_list, details, auth_login, auth_signup
from apps.fnc_container import components
from flask_login import current_user, logout_user

app.layout = html.Div([
    html.Div(id='logout'),
    dcc.Store(id='filtred_cards'), 
    dcc.Store(id='filtred_cards_tmp'), 
    dcc.Store(id='input_data', storage_type='session'), 
    dcc.Store(id='historical_subtraction'),
    dcc.Store(id='substruct_items'),
    dcc.Store(id='gang_notifier'),
    dcc.Store(id='isFiltered'),
    dcc.Store(id='start_data_holder'),
    dcc.Location(id='url', refresh=False),
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
        return details.build_page_2(), components.build_a_link(pathname, current_user)
    
    else:
        return html.H3('404 "URL not found"'), components.build_a_link(pathname, current_user)
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=False)