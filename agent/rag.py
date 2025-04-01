from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pdfplumber
import io


class RAG(object):
    def __init__(self, content: io.BytesIO, filetype):
        self.vectorstore = None
        self.content = content
        self.retriever = None
        self.rag_chain = None
        self.initialize(filetype)


    def initialize(self,filetype):
        docs = []

        if filetype == 'pdf':
            with pdfplumber.open(self.content) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        docs.append(text)

        elif filetype == 'txt':
            text = self.content.read().decode("utf-8")
            splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1000,     # Maximum number of characters per chunk
                            chunk_overlap=100,   # Overlap between chunks to maintain context
                            length_function=len, # Function to measure chunk length
                            is_separator_regex=False, # Whether separators are regex patterns,
                            separators=[
                                "\n\n",
                                "\n",
                                " ",
                                ".",
                                ",",
                                "\u200b",  # Zero-width space
                                "\uff0c",  # Fullwidth comma
                                "\u3001",  # Ideographic comma
                                "\uff0e",  # Fullwidth full stop
                                "\u3002",  # Ideographic full stop
                                "",
                            ],
                        )
            docs = splitter.split_text(text)

        else:
            raise ValueError("Unsupported file type: only .pdf and .txt are supported.")


        self.vectorstore = Chroma.from_texts(docs, embedding=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.6, "k": 1})


    def retrieve(self, query):
        docs = self.retriever.invoke(query)
        if len(docs) == 0:
            return 'No relevant context retrieved.'
        docs = [doc.page_content for doc in docs]
        context = '\n\n'.join(docs)
        return context

    def clean(self):
        self.vectorstore.delete_collection()
