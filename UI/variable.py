class Variables(object):
    def __init__(self):
        self.df = None
        self.agent = None
        self.rag = None
        self.rag_prompt = None
        self.use_rag = False
        self.dialog = []


global_vars = Variables()
