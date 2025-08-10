class APP_State(object):
    def __init__(self):
        self.df = None
        self.agent = None
        self.rag = None
        self.dialog = []
        self.file_name = None
        self.suggested_questions = None
        self.data_snapshots = []
        self.conversation_session = None
        self.target_attr = ""
        self.current_stage = "Identify"
        self.editor_id_counter = 0
        self.bias_identifier_counter = 0


app_vars = APP_State()
