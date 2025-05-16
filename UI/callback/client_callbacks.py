from UI.app import app
from dash import html, dcc, Input, Output, ClientsideFunction, State, Input, Output, MATCH
import dash_bootstrap_components as dbc
import json
# Enable automatically scrolling down of the chat box
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

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            document.getElementById('upload-data').querySelector('input').click();
        }
    }
    """,
    Output('output-placeholder', "data-dummy"),  # Dummy output, necessary but not used
    Input('menu-import-data', 'n_clicks')
)

# callback for showing a spinner within dbc.Button()
app.clientside_callback(
    """
    function (click) {
        return [""" + json.dumps(dbc.Spinner(size='sm').to_plotly_json()) + """, " Running..."]
    }
    """,
    Output({'type': 'spinner-btn', 'index': MATCH}, 'children'),
    Input({'type': 'spinner-btn', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function (click) {
        return [""" + json.dumps(dbc.Spinner(size='sm').to_plotly_json()) + """, " Analyzing..."]
    }
    """,
    Output({'type': 'report-table-button', 'index': MATCH}, 'children'),
    Input({'type': 'report-table-button', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function (click) {
        return [""" + json.dumps(dbc.Spinner(size='sm').to_plotly_json()) + """, " Analyzing..."]
    }
    """,
    Output({'type': 'llm-media-button', 'index': MATCH}, 'children'),
    Input({'type': 'llm-media-button', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)


app.clientside_callback(
    """
    function (click) {
        return [""" + json.dumps(dbc.Spinner(size='sm').to_plotly_json()) + """, " Analyzing..."]
    }
    """,
    Output({'type': 'report-graph-button', 'index': MATCH}, 'children'),
    Input({'type': 'report-graph-button', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks % 2 === 1) {
            return "button-clicked";
        }
        return "button-released";
    }
    """,
    Output("rag-button", "className"),
    Input("rag-button", "n_clicks")
)