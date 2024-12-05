from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pdfplumber


class RAG(object):
    def __init__(self, content):
        self.vectorstore = None
        self.content = content
        self.retriever = None
        self.rag_chain = None
        self.load()
        self.build_chain()

    def load(self):
        docs = []
        with pdfplumber.open(self.content) as pdf:
            for page in pdf.pages:
                docs.append(page.extract_text())
        # Create OpenAI embeddings
        self.vectorstore = Chroma.from_texts(docs,
                                             embedding=OpenAIEmbeddings())  # from_documents(documents=docs, embedding=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever()

    def build_chain(self):
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        prompt = hub.pull("rlm/rag-prompt")
        self.rag_chain = (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | prompt)

    def invoke(self, query):
        return self.rag_chain.invoke(query)

    def clean(self):
        self.vectorstore.delete_collection()
