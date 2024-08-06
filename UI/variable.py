from agent import DatasetAgent

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


global_vars = Variables()
