import dash
import dash_bootstrap_components as dbc
import configparser
import sys, os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def read_configs(file_path='config.ini'):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    # Read the config.ini file
    config.read(file_path)
    # Access the api_key from the 'settings' section
    error_msg = """Please configure your openai api_key or database url in the file config.ini before running the program.
        
        The config.ini under the root directory of this project should have the following format:
        
        [settings]
        api_key = your_openai_api_key
        database_url = your_postgres_db_url_here
        
        """
    try:
        api_key = config['settings']['api_key']
        database_url = config['settings']['database_url']
    except KeyError:
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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)

server.config['SQLALCHEMY_DATABASE_URI'] = os.environ['BIASNAVI_DATABASE_URL']

db: SQLAlchemy = SQLAlchemy(server)
