import configparser
from UI.app import app
from UI.callback import callbacks
from UI.layout.home_layout import get_layout
from dash.dependencies import Input, Output
import os
import sys
from getpass import getpass
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage

def read_api_key(file_path='config.ini'):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    # Read the config.ini file
    config.read(file_path)
    # Access the api_key from the 'settings' section
    try:
        api_key = config['settings']['api_key']
    except KeyError:
        print("Please configure your openai api_key in the file config.ini before runing the program.")
        sys.exit(1)
    return api_key


if __name__ == '__main__':
    api_key = read_api_key()
    os.environ["OPENAI_API_KEY"] = api_key
    # compas = COMPASDataset()
    # data_agent = DatasetAgent(compas.get_dataframe())
    app.layout = get_layout()
    app.clientside_callback(
        """
        function(children) {
            var contentArea = document.getElementById('query-area');
            setTimeout(function() { contentArea.scrollTop = contentArea.scrollHeight; }, 100);
        }
        """,
        Output("query-area", "data-dummy"),
        Input("query-area", "children")
    )
    app.run_server(debug=True)
    # print("Now you can query the dataset and manage the bias. Enter exit to end the program.")
    # query=''
    # while query!="exit":
    #     query = input("Please enter:")
    #     data_agent.run(query)
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", max_tokens=1024)
    # messages = [
    #     SystemMessage(
    #         content="You are a helpful assistant that translates English to French."
    #     ),
    #     HumanMessage(
    #         content="Translate this sentence from English to French. I love programming."
    #     ),
    # ]




