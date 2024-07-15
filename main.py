from UI.app import app, db, server
from utils import *
from UI.callback import callbacks, client_callbacks
from UI.layout.home_layout import get_layout
import sys

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

    app.layout = get_layout()

    # Run the server
    app.run(debug=True,dev_tools_hot_reload=False)
