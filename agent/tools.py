import ast
from contextlib import redirect_stdout
from langchain.pydantic_v1 import BaseModel, Field
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


class CustomizedPythonAstREPLTool(PythonAstREPLTool):

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
        processed_item.subplots_adjust(bottom=0.4)
        processed_item.savefig(buf, format="png")
        processed_item.close()
        data = base64.b64encode(buf.getbuffer()).decode("utf8")
        buf.close()

        current_id = len(self.elem_queue)
        self.elem_queue.append(html.Div([
            html.Img(src=f"data:image/png;base64,{data}",
                     style={'maxWidth': '100%', 'cursor': 'pointer'})
        ], id={"type": "llm-media-figure", "index": current_id}, className="llm-media-figure"))

        self.elem_queue.append(dbc.Modal([
            dbc.ModalHeader("LLM Chart"),
            dbc.ModalBody(html.Div([
                html.Img(src=f"data:image/png;base64,{data}",
                         style={'maxWidth': '100%'})
            ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
            dbc.ModalFooter()
        ], id={"type": "llm-media-modal", "index": current_id}, centered=True, className="figure-modal", size="lg"))

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
    ) -> str:
        try:
            self.execution_error.clear()
            
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
                    else:
                        raise NotImplementedError(
                            "The LLM returned an unsupported media type.")
                    if processed_item is None:
                        return io_buffer.getvalue()
                    else:
                        return processed_item
            except Exception as eval_exception:
                if not re.search("\w\s*=", module_end_str):
                    self.execution_error.append(eval_exception)
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals, self.locals)
                return io_buffer.getvalue()
        except Exception as eval_exception:
            if not re.search("\w\s*=", module_end_str):
                self.execution_error.append(eval_exception)
            return "{}: {}".format(type(eval_exception).__name__, str(eval_exception))
