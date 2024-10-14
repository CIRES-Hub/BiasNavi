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
from UI.callback.report_callbacks import *
from UI.callback.wizard_callbacks import *
from UI.callback.chat_mode_callbacks import *
from UI.callback.prompt_callbacks import *

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
# from langchain_core.messages import HumanMessage
# from langchain_openai import ChatOpenAI
#
#
# import base64
# import os
# import httpx
# os.environ["OPENAI_API_KEY"] = "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"
# model = ChatOpenAI(model="gpt-4o")
# image_url = "./UI/assets/cat.jpg"
# with open(image_url, "rb") as image_file:
#     # Read the binary content of the image
#     image_data = base64.b64encode(image_file.read()).decode('utf-8')
# message = HumanMessage(
#     content=[
#         {"type": "text", "text": "describe the image"},
#         {
#             "type": "image_url",
#             "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
#         },
#     ],
# )
# response = model.invoke([message])
# print(response.content)