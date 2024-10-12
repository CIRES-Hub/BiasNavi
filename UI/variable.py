from agent import DatasetAgent
import time

class Variables(object):
    def __init__(self):
        self.df = None
        self.agent: DatasetAgent = None
        self.rag = None
        self.rag_prompt = None
        self.use_rag = False
        self.dialog = []
        self.file_name = None
        self.suggested_questions = None
        self.data_snapshots = []
        self.conversation_session = round(time.time() * 1000)

global_vars = Variables()