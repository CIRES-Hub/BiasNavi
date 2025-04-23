from agent import DatasetAgent
import time


class Variables(object):
    def __init__(self):
        self.df = None
        self.agent: DatasetAgent = None
        self.rag = None
        self.dialog = []
        self.file_name = None
        self.suggested_questions = None
        self.data_snapshots = []
        self.conversation_session = None
        self.label = ""
        self.current_stage = "Identify"



global_vars = Variables()
