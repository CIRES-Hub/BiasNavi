from UI.app import app, server
from db_models.users import db
from db_models import *
from UI.callback import callbacks, client_callbacks,menu_callbacks
import sys
from dash import dcc, html, Input, Output
import dash

if __name__ == '__main__':
    # Init tables
    try:
        with server.app_context():
            db.create_all()
            db.session.commit()
    except Exception as e:
        print(str(e))
        sys.stdout.flush()
        with server.app_context():
            db.session.rollback()

    # Run the server
    # Disable reloader due to errors while writing temp data for sandboxes
    app.run(debug=True, use_reloader=False, dev_tools_hot_reload=False)
