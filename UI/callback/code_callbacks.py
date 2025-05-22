import dash
import docker.errors
import logging
from UI.app import app
from dash.dependencies import Input, Output, State
from agent import DatasetAgent
from dash import html
import pandas as pd
from UI.functions import *
from flask_login import current_user
import docker
import os
import shutil
import time
import random
from UI.functions import get_docker_client
code_logger = logging.getLogger(__name__)




@app.callback(
    [Output("console-area", "children"),
     Output("commands-input", "disabled", allow_duplicate=True),
     Output('table-overview', 'data', allow_duplicate=True),
     Output('table-overview', 'columns', allow_duplicate=True),
     Output('column-names-dropdown', 'options', allow_duplicate=True),
     Output('data-alert', 'children', allow_duplicate=True),
     Output('data-alert', 'is_open', allow_duplicate=True),
     Output("python-code-console","style", allow_duplicate=True),
    Output({'type': 'spinner-btn', 'index': 9}, 'children', allow_duplicate=True),
     ],
    Input({'type': 'spinner-btn', 'index': 9}, "children"),
    State("commands-input", "value"),
    prevent_initial_call=True
)
def execute_commands(n_click, commands):
    if global_vars.df is None:
        return ["Have you imported a dataset and entered a query?", False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update ,"Run"]
    if commands is not None:
        try:
            print("Running sandbox...")
            user_id = str(current_user.id)
            current_path = os.path.dirname(os.path.realpath(__file__))
            parent_path = os.path.dirname(current_path)
            user_data_dir = os.path.join(os.path.dirname(parent_path), 'tmp', user_id)

            if not os.path.exists(user_data_dir):
                print("Creating user's directory...")
                os.makedirs(user_data_dir, exist_ok=True)
                shutil.copyfile(os.path.join(parent_path, 'assets', 'sandbox_main.py'),
                                os.path.join(user_data_dir, 'sandbox_main.py'))
                print("Create user's directory successfully")
            else:
                if not os.path.exists(os.path.join(user_data_dir, 'sandbox_main.py')):
                    shutil.copyfile(os.path.join(parent_path, 'assets', 'sandbox_main.py'),
                                    os.path.join(user_data_dir, 'sandbox_main.py'))

            user_output_file = os.path.join(user_data_dir, f"_output_{user_id}.out")
            user_error_file = os.path.join(user_data_dir, f"_error_{user_id}.err")
            container_name = 'biasnavi-' + user_id

            with open(os.path.join(user_data_dir, 'sandbox_commands.py'), "w") as f:
                f.write(commands)

            global_vars.df.to_csv(os.path.join(user_data_dir, "df.csv"), index=False)
            if os.path.exists(user_output_file):
                os.remove(user_output_file)
            if os.path.exists(user_error_file):
                os.remove(user_error_file)

            client = get_docker_client()
            print("Running commands inside container")
            try:
                user_container = client.containers.get(container_name)
            except docker.errors.NotFound:
                print(f"Container {container_name} not found. Creating...")
                client.containers.run(
                    'daisyy512/hello-docker',
                    name=container_name,
                    volumes={user_data_dir: {'bind': f'/home/sandbox/{user_id}', 'mode': 'rw'}},
                    detach=True,
                    tty=True
                )
                user_container = client.containers.get(container_name)
            user_container.exec_run(cmd="python sandbox_main.py " + user_id, workdir='/home/sandbox/' + user_id)
            print("Run commands inside container successfully")

            output = []
            if os.path.isfile(user_output_file):
                with open(user_output_file, "r") as f:
                    for line in f:
                        output.append(html.P(line, style={"color": "black"}))

            if os.path.isfile(user_error_file):
                with open(user_error_file, "r") as f:
                    for line in f:
                        output.append(html.P(line, style={"color": "red"}))
            
            new_df = pd.read_csv(os.path.join(user_data_dir, "df.csv"))
            global_vars.df = new_df
            global_vars.conversation_session = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
            global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name, conversation_session=global_vars.conversation_session)
            
            return [output, 
                    False,
                    global_vars.df.to_dict('records'),
                    [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
                    [{'label': col, 'value': col} for col in global_vars.df.columns], "The data might have been changed.", True, {"display":"block"},"Run"]

        except Exception as e:
            if isinstance(e, docker.errors.NotFound):
                try:
                    print("Recreate container")
                    client = docker.from_env()
                    container_name = 'biasnavi-' + user_id
                    client.containers.run('daisyy512/hello-docker',
                                          name=container_name,
                                          volumes=[user_data_dir + ':/home/sandbox/' + user_id],
                                          detach=True,
                                          tty=True)
                    print("Create container successfully")
                    user_container = client.containers.get(container_name)
                    user_container.exec_run(cmd="python sandbox_main.py " + user_id, workdir='/home/sandbox/' + user_id)
                    output = []
                    if os.path.isfile(user_output_file):
                        with open(user_output_file, "r") as f:
                            for line in f:
                                output.append(html.P(line, style={"color": "black"}))

                    if os.path.isfile(user_error_file):
                        with open(user_error_file, "r") as f:
                            for line in f:
                                output.append(html.P(line, style={"color": "red"}))
                            
                    new_df = pd.read_csv(os.path.join(user_data_dir, "df.csv"))
                    global_vars.df = new_df
                    global_vars.conversation_session = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
                    global_vars.agent = DatasetAgent(global_vars.df, file_name=global_vars.file_name, conversation_session=global_vars.conversation_session)
            
                    return [output, 
                            False,
                            global_vars.df.to_dict('records'),
                            [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
                            [{'label': col, 'value': col} for col in global_vars.df.columns],dash.no_update, dash.no_update,dash.no_update, "Run"]

                except Exception as e:
                    print("Create container failed: ", e)
                    return ["Sandbox is not available", False, False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update, "Run"]
            elif isinstance(e, docker.errors.APIError):
                if e.status_code is not None and e.status_code == 409:
                    user_container = client.containers.get(container_name)
                    print("Restart container")
                    user_container.start()
                    user_container.exec_run(cmd="python sandbox_main.py " + user_id, workdir='/home/sandbox/' + user_id)

                    output = []
                    if os.path.isfile(user_output_file):
                        with open(user_output_file, "r") as f:
                            for line in f:
                                output.append(html.P(line, style={"color": "black"}))

                    if os.path.isfile(user_error_file):
                        with open(user_error_file, "r") as f:
                            for line in f:
                                output.append(html.P(line, style={"color": "red"}))
                    return [output, 
                            False,
                            global_vars.df.to_dict('records'),
                            [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in global_vars.df.columns],
                            [{'label': col, 'value': col} for col in global_vars.df.columns], dash.no_update, dash.no_update,dash.no_update,"Run"]

                return [str(e),  False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update,"Run"]
            else:
                code_logger.error(type(e))
                code_logger.error(e)
                return [str(e),  False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update,"Run"]
    return [dash.no_update,  False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,dash.no_update,"Run"]


