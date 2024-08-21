import ast
from contextlib import redirect_stdout
from io import StringIO
import pandas as pd
import os
from os.path import basename
import sys

if __name__ == '__main__':
    try:
        user_id = sys.argv[1]
        df = pd.read_csv("df.csv")
        with open('sandbox_commands.py', 'r') as file:
            commands = file.read()
            
        tree = ast.parse(commands)
        io_buffer = StringIO()
        with redirect_stdout(io_buffer):
            module = ast.Module(tree.body, type_ignores=[])
            exec(ast.unparse(module), {}, {"df": df})  # type: ignore
        # print out 
        with open(f"_output_{user_id}.out", "w") as f:
            f.write(io_buffer.getvalue())
    except Exception as e:
        with open(f"_output_{user_id}.out", "w") as f:
            f.write("{}: {}".format(type(e).__name__, str(e)))
