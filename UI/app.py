import dash
import dash_bootstrap_components as dbc
import sys
import os
from flask import Flask, redirect
from db_models.users import db, User
from flask_login import LoginManager, current_user
from dash import Input, Output, dcc, html
from uuid import UUID
import yaml


def read_configs(file_path='config.yml'):
    # Load the YAML file
    error_msg = """Please configure your openai api_key or database url in the file config.yml before running the program.

        The config.yml under the root directory of this project should have the following format:

        settings:
          api_key: your_openai_api_key
          database_url: your_postgres_db_url_here

        """
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)

        # Access the api_key and database_url from the 'settings' section
        api_key = config['settings']['api_key']
        database_url = config['settings']['database_url']
    except (KeyError, FileNotFoundError, yaml.YAMLError):
        print(error_msg)
        sys.exit(1)

    if api_key.strip() == '' or database_url.strip() == '':
        print(error_msg)
        sys.exit(1)

    return api_key, database_url


api_key, database_url = read_configs()
os.environ["OPENAI_API_KEY"] = api_key
os.environ["BIASNAVI_DATABASE_URL"] = database_url

server = Flask(__name__)
server.secret_key = "supersecret"
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = None


@login_manager.user_loader
def load_user(user_id):
    try:
        uuid_obj = UUID(user_id)
        return User.query.filter_by(id=uuid_obj).first()
    except ValueError:
        return None


app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"], server=server, use_pages=True,
                url_base_pathname='/', suppress_callback_exceptions=True)

# Add this layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dash.page_container
])

server.config['SQLALCHEMY_DATABASE_URI'] = os.environ['BIASNAVI_DATABASE_URL']

db.init_app(server)


# @server.route('/')
# def index_redirect():
#     return redirect('/login')


@app.callback(
    Output('page-container', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def display_page(pathname):
    if pathname == '/' or pathname == '/signup':
        if current_user.is_authenticated:
            return dcc.Location(pathname='/home', id='redirect-to-home', refresh=True)
        return dash.page_container
    return dash.page_container
