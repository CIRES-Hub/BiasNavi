import dash
import dash_bootstrap_components as dbc



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])




# class BiasNaviUI:
#
#     def __init__(self, title='BiasNavi', description='Navigate your way through biases in your data'):
#         # Set the title and description
#         self.title = title
#         self.description = description
#
#
#     def run(self):
#         self.app.run_server(debug=True)
