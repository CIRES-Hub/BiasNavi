from UI.app import app, server
from db_models.users import db
import sys
from UI.callback.code_callbacks import *
from UI.callback.menu_callbacks import *
from UI.callback.user_callbacks import *
from UI.callback.data_callbacks import *
from UI.callback.chat_callbacks import *
from UI.callback.client_callbacks import *
from UI.callback.user_callbacks import *
from UI.callback.bias_callbacks import *
from UI.callback.wizard_callbacks import *
from UI.callback.prompt_callbacks import *
from UI.callback.widget_callbacks import *
from UI.callback.view_callbacks import *

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






