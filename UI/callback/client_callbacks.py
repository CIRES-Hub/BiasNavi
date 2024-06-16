from UI.app import app
from dash import html, dcc, Input, Output, ClientsideFunction, State

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