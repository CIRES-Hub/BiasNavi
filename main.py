from UI.app import app, server
import logging
from functools import wraps
from dash import callback_context
from datetime import datetime
def log_callback(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ctx = callback_context
            if ctx.triggered:
                triggered = ctx.triggered[0].get("prop_id", "")

                # Skip logging if noisy component triggered
                if any(x in triggered for x in [".data", ".value", ".pathname", ".n_intervals"]):
                    return func(*args, **kwargs)

                logger.info(f"CALLBACK TRIGGERED by: {triggered}")

                str_args = str(args)
                if len(str_args) > 500:
                    str_args = str_args[:500] + "..."
                logger.info(f"INPUT ARGS: {str_args}")
        except Exception as e:
            logger.warning(f"Failed to log callback context: {e}")

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(f"Callback exception: {e}")
            raise

    return wrapper


# Configure logging (to file or console)
now_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"dash_callbacks_{now_str}.log"),  # Log to file
        logging.StreamHandler()                     # Log to console
    ]
)

logger = logging.getLogger(__name__)

_original_callback = app.callback

def logging_callback(*args, **kwargs):
    def wrapper(func):
        return _original_callback(*args, **kwargs)(log_callback(func))
    return wrapper

app.callback = logging_callback

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






