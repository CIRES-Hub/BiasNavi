import configparser
from UI.app import app
from UI.callback import callbacks, client_callbacks
from UI.layout.home_layout import get_layout
from dash.dependencies import Input, Output
import os
import sys


def read_api_key(file_path='config.ini'):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    # Read the config.ini file
    config.read(file_path)
    # Access the api_key from the 'settings' section
    try:
        api_key = config['settings']['api_key']
    except KeyError:
        print("""Please configure your openai api_key in the file config.ini before runing the program.
        
        The config.ini under the root directory of this project should have the following format:
        
        [settings]
        api_key = your_openai_api_key
        
        """)
        sys.exit(1)
    return api_key


if __name__ == '__main__':
    api_key = read_api_key()
    os.environ["OPENAI_API_KEY"] = api_key
    app.layout = get_layout()

    # Run the server
    app.run_server(debug=True)
