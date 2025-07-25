import ast
from contextlib import redirect_stdout
from pydantic import BaseModel, Field
from io import StringIO
from typing import Optional, Type
from langchain_experimental.tools.python.tool import PythonAstREPLTool, sanitize_input
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from typing import Any, Dict, List, Union
from types import ModuleType
from dash import dash_table, dcc, html
from plotly.tools import mpl_to_plotly
from pandas import DataFrame
from matplotlib.figure import Figure
import traceback
import io
import base64
import dash_bootstrap_components as dbc
import matplotlib
import re
matplotlib.use('Agg')
import time



class Graph_Table_Generator(PythonAstREPLTool):
    name: str = "Run_Python_Code"
    description: str = "A Python shell. Use this to execute python commands, especially when asked to draw a plot or generate a table"
    response_format: str = "content_and_artifact"

    elem_queue: list = Field(default_factory=list)
    execution_error: list[Exception] = []
    list_commands: list[str] = []

    def __init__(self, elem_queue, execution_error, list_commands, **kwargs):
        super(PythonAstREPLTool, self).__init__(**kwargs)
        self.elem_queue = elem_queue
        self.execution_error = execution_error
        self.list_commands = list_commands

    def add_figure(self, processed_item: Figure):

        buf = io.BytesIO()
        # Automatically adjust layout
        processed_item.tight_layout()
        processed_item.subplots_adjust(bottom=0.1)
        processed_item.savefig(buf, format="png", bbox_inches="tight")
        data = base64.b64encode(buf.getbuffer()).decode("utf8")
        buf.close()

        current_id = int(time.time())
        figure = html.Div([
            html.Div(
                [
                    html.I(
                        className="bi bi-chevron-down",
                        id={"type": "toggle-msg-icon", "index": current_id},
                        style={
                            "cursor": "pointer",
                            "marginRight": "8px",
                            "fontSize": "1.2rem"
                        }
                    ),
                    html.H5(
                        "Figure",
                        style={"margin": 0}
                    )
                ],
                id={"type": "toggle-msg-btn", "index": current_id},
                style={
                    "display": "flex",
                    "alignItems": "center"
                }
            ),
            dbc.Collapse(
                [
                    html.Div([
                        html.Img(
                            src=f"data:image/png;base64,{data}",
                            style={
                                'maxWidth': '100%',
                                'cursor': 'pointer',
                                'display': 'block'
                            },
                            id={"type": "llm-generated-chart", "index": current_id}
                        ),
                        html.Div(
                            dbc.Button(
                                "Explain",
                                id={"type": "llm-media-button", "index": current_id},
                                className="primary-button",
                                n_clicks=0
                            ),
                            style={
                                'display': 'flex',
                                'justifyContent': 'flex-end',
                                'marginTop': '10px'
                            }
                        )
                    ]),
                    html.Div([
                    ], id={"type": "llm-media-explanation", "index": current_id}, style={"display": "none"})
                ],
                id={"type": "collapse-msg", "index": current_id},
                is_open=True
            )
        ], className="section")
        self.elem_queue.append(figure)
        return self.elem_queue



    def add_table(self, processed_item: DataFrame):
        self.elem_queue.append(dash_table.DataTable(page_size=25, page_action='native',
                                                    style_cell={
                                                        'textAlign': 'center', 'fontFamiliy': 'Arial'},
                                                    style_header={'backgroundColor': '#614385', 'color': 'white',
                                                                  'fontWeight': 'bold'
                                                                  }, style_table={'overflowX': 'auto'}, data=processed_item.to_dict('records')))

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    )-> tuple:
        try:
            self.execution_error.clear()
            self.elem_queue.clear()
            self.list_commands.clear()

            if self.sanitize_input:
                query = sanitize_input(query)
            module_end_str=""
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), self.globals, self.locals)  # type: ignore
            print(ast.unparse(ast.Module(tree.body, type_ignores=[])))
            self.list_commands.append(ast.unparse(ast.Module(tree.body, type_ignores=[])))
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    processed_item = eval(module_end_str.replace(
                        '.show()', ''), self.globals, self.locals)
                    if (isinstance(processed_item, DataFrame)):
                        self.add_table(processed_item)
                    elif ((isinstance(processed_item, ModuleType) and processed_item.__name__ == 'matplotlib.pyplot')
                            or isinstance(processed_item, Figure)):
                        self.add_figure(processed_item)
                    # else:
                    #     raise NotImplementedError(
                    #         "The LLM returned an unsupported media type.")
                    if processed_item is None:
                        return 'None', io_buffer.getvalue()
                    else:
                        return "The plot has been generated.", processed_item
            except Exception as eval_exception:
                if not re.search(r"\w\s*=", module_end_str):
                    self.execution_error.append(eval_exception)
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals, self.locals)
                return 'Exception',io_buffer.getvalue()
        except Exception as eval_exception:
            if not re.search(r"\w\s*=", module_end_str):
                self.execution_error.append(eval_exception)
            return 'Exception',"{}: {}".format(type(eval_exception).__name__, str(eval_exception))
