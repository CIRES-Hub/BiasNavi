from UI.app import app, server
from db_models.users import db
from db_models import *
from UI.callback import callbacks, client_callbacks,menu_callbacks
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

    # Run the server
    app.run(debug=True,dev_tools_hot_reload=False)
