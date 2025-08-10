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
from dash import MATCH, ALL
from UI.functions import get_docker_client

code_logger = logging.getLogger(__name__)


def prepare_user_dir(user_id, parent_path):
    user_data_dir = os.path.join(os.path.dirname(parent_path), 'tmp', user_id)
    os.makedirs(user_data_dir, exist_ok=True)
    sandbox_main_path = os.path.join(parent_path, 'assets', 'sandbox_main.py')
    target_main_path = os.path.join(user_data_dir, 'sandbox_main.py')
    if not os.path.exists(target_main_path):
        shutil.copyfile(sandbox_main_path, target_main_path)
    return user_data_dir


def collect_output(output_path, error_path):
    output = []
    if os.path.isfile(output_path):
        with open(output_path, "r") as f:
            output.extend([html.P(line, style={"color": "black"}) for line in f])
    if os.path.isfile(error_path):
        with open(error_path, "r") as f:
            output.extend([html.P(line, style={"color": "red"}) for line in f])
    else:
        output.extend([html.P("The code was executed successfully.", style={"color": "green"})])
    return output


def run_in_container(client, container_name, user_id, user_data_dir):
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        container = client.containers.run(
            'daisyy512/hello-docker',
            name=container_name,
            volumes={user_data_dir: {'bind': f'/home/sandbox/{user_id}', 'mode': 'rw'}},
            detach=True,
            tty=True
        )
    container.exec_run(cmd=f"python sandbox_main.py {user_id}", workdir=f'/home/sandbox/{user_id}')
    return container


@app.callback(
    [Output("console-area", "children"),
     Output("commands-input", "disabled", allow_duplicate=True),
     Output('table-overview', 'data', allow_duplicate=True),
     Output('table-overview', 'columns', allow_duplicate=True),
     Output('column-names-dropdown', 'options', allow_duplicate=True),
     Output('data-alert', 'children', allow_duplicate=True),
     Output('data-alert', 'is_open', allow_duplicate=True),
     Output("python-code-console", "style", allow_duplicate=True),
     Output({'type': 'spinner-btn', 'index': 9}, 'children', allow_duplicate=True)],
    Input({'type': 'spinner-btn', 'index': 9}, "children"),
    State("commands-input", "value"),
    prevent_initial_call=True
)
def execute_commands(n_click, commands):
    if app_vars.df is None:
        return ["Have you imported a dataset and entered a query?", False, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Run"]

    if not commands:
        return [dash.no_update] * 8 + ["Run"]

    try:
        print("Running sandbox...")
        user_id = str(current_user.id)
        current_path = os.path.dirname(os.path.realpath(__file__))
        parent_path = os.path.dirname(current_path)
        user_data_dir = prepare_user_dir(user_id, parent_path)

        user_output_file = os.path.join(user_data_dir, f"_output_{user_id}.out")
        user_error_file = os.path.join(user_data_dir, f"_error_{user_id}.err")
        container_name = 'biasnavi-' + user_id

        with open(os.path.join(user_data_dir, 'sandbox_commands.py'), "w") as f:
            f.write(commands)

        app_vars.df.to_csv(os.path.join(user_data_dir, "df.csv"), index=False)
        for file in [user_output_file, user_error_file]:
            if os.path.exists(file):
                os.remove(file)

        client = get_docker_client()
        try:
            run_in_container(client, container_name, user_id, user_data_dir)
        except docker.errors.APIError as e:
            if e.status_code == 409:  # container exists but stopped
                container = client.containers.get(container_name)
                container.start()
                container.exec_run(cmd=f"python sandbox_main.py {user_id}", workdir=f'/home/sandbox/{user_id}')
            else:
                raise

        output = collect_output(user_output_file, user_error_file)
        new_df = pd.read_csv(os.path.join(user_data_dir, "df.csv"))
        app_vars.df = new_df
        app_vars.conversation_session = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
        app_vars.agent = DatasetAgent(app_vars.df, file_name=app_vars.file_name,
                                      conversation_session=app_vars.conversation_session)

        columns = [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in app_vars.df.columns]
        options = [{'label': col, 'value': col} for col in app_vars.df.columns]

        if ("df =" in commands or "df=" in commands) and "successfully" in output[-1].children:
            return [output, False, app_vars.df.to_dict('records'), columns, options,
                    "The data might have been changed.", True, {"display": "block"}, "Run"]
        else:
            return [output, False, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, False, {"display": "block"}, "Run"]

    except Exception as e:
        code_logger.error(e)
        return [f"Error: {str(e)}", False] + [dash.no_update] * 6 + ["Run"]


@app.callback(
    Output({'type': "console-area", 'index': MATCH}, "children"),
    Output({'type': "commands-input", 'index': MATCH}, "disabled"),
    Output({'type': "python-code-console", 'index': MATCH}, "style"),
    Output({'type': 'execute-code-btn', 'index': MATCH}, "style"),
    Output({'type': 'is-code-executed', 'index': MATCH}, "data"),
    Input({'type': 'execute-code-btn', 'index': MATCH}, "n_clicks"),
    State({'type': "commands-input", 'index': MATCH}, "value"),
    prevent_initial_call=True
)
def execute_generated_code(n_click, commands):
    if app_vars.df is None:
        return ["Have you imported a dataset and entered a query?", False, dash.no_update, dash.no_update,
                dash.no_update]

    if not commands:
        return [dash.no_update] * 5

    try:
        print("Running sandbox...")
        user_id = str(current_user.id)
        current_path = os.path.dirname(os.path.realpath(__file__))
        parent_path = os.path.dirname(current_path)
        user_data_dir = prepare_user_dir(user_id, parent_path)

        # File paths
        user_output_file = os.path.join(user_data_dir, f"_output_{user_id}.out")
        user_error_file = os.path.join(user_data_dir, f"_error_{user_id}.err")
        container_name = 'biasnavi-' + user_id

        # Save code
        with open(os.path.join(user_data_dir, 'sandbox_commands.py'), "w") as f:
            f.write(commands)

        # Save input dataframe
        app_vars.df.to_csv(os.path.join(user_data_dir, "df.csv"), index=False)

        # Clean up old outputs
        for file in [user_output_file, user_error_file]:
            if os.path.exists(file):
                os.remove(file)

        # Docker execution
        client = get_docker_client()
        try:
            run_in_container(client, container_name, user_id, user_data_dir)
        except docker.errors.APIError as e:
            if e.status_code == 409:
                container = client.containers.get(container_name)
                container.start()
                container.exec_run(cmd=f"python sandbox_main.py {user_id}", workdir=f"/home/sandbox/{user_id}")
            else:
                raise

        # Collect results
        output = collect_output(user_output_file, user_error_file)

        # Reload updated df
        new_df = pd.read_csv(os.path.join(user_data_dir, "df.csv"))
        app_vars.df = new_df

        # Reset agent session
        app_vars.conversation_session = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
        app_vars.agent = DatasetAgent(
            app_vars.df,
            file_name=app_vars.file_name,
            conversation_session=app_vars.conversation_session
        )
        if ("df =" in commands or "df=" in commands) and "successfully" in output[-1].children:
            return [output, False, {"display": "block"}, {"display": "none"}, "1"]
        else:
            return [output, False, {"display": "block"}, {"display": "none"}, "0"]

    except Exception as e:
        code_logger.error(e)
        return [f"Error: {str(e)}", False, dash.no_update, dash.no_update, dash.no_update]


@app.callback(
    Output('table-overview', 'data', allow_duplicate=True),
    Output('table-overview', 'columns', allow_duplicate=True),
    Input({'type': 'is-code-executed', 'index': ALL}, "data"),
    prevent_initial_call=True
)
def update_table_after_executing_code(data):
    if not data or any(d != "1" for d in data):
        return dash.no_update, dash.no_update

    columns = [{"name": col, "id": col, 'deletable': True, 'renamable': True} for col in app_vars.df.columns]
    return app_vars.df.to_dict('records'), columns,


@app.callback(
    Output({'type': 'execute-code-btn', 'index': MATCH}, "style", allow_duplicate=True),
    Input({'type': "commands-input", 'index': MATCH}, "value"),
    prevent_initial_call=True
)
def reactive_run_button(commands):
    return {"display": "block"}
