from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages.base import messages_to_dict
import pandas as pd
import os
import time
from enum import Enum
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import ConfigurableField
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from agent.utils import create_pandas_dataframe_agent
from db_models.conversation import Conversation
from db_models.system_log import SystemLogMessage
import re


class ConversationFormat(str, Enum):
    FULL_JSON = 'Full JSON'
    SIMPLIFIED_JSON = 'Simplified JSON'
    TEXT = 'Text'


class PersistenceType(str, Enum):
    DATABASE = 'Database'
    FILE = 'File'


class LLMModel(str, Enum):
    GPT4o = 'gpt4o'
    GPT4 = 'gpt4'
    GPT4omini = 'gpt4omini'


class DatasetAgent:

    def __init__(self, df, llm=None, file_name=None, user_id=None):
        self.user_id = user_id
        if llm is None:
            llm = ChatOpenAI(temperature=0.5, model="gpt-4o-mini").configurable_alternatives(
                ConfigurableField(id="llm"),
                default_key="gpt-4o-mini",
                gpt4omini=ChatOpenAI(model="gpt-4o-mini"),
                gpt4=ChatOpenAI(model="gpt-4-turbo"),
                gpt4o=ChatOpenAI(model="gpt-4o"),
            )
        self.llm = llm
        self.model_name = llm.model_name
        self.session_id = round(time.time() * 1000)
        self.elem_queue = []
        self.execution_error: list[Exception] = []
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert in dealing with bias in datasets for data science. "
                    "Your expertise includes identifying, measuring, and mitigating biases in tabular datasets. "
                    "You are well-versed in advanced statistical methods, machine learning techniques, and ethical considerations for fair AI. "
                    "You can provide detailed explanations of bias detection methods, offer actionable recommendations for bias mitigation, "
                    "and guide users through complex scenarios with step-by-step instructions. "
                    "Your goal is to ensure datasets are fair, transparent, and robust for accurate and equitable AI model/business development."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            verbose=True,
            elem_queue=self.elem_queue,
            execution_error=self.execution_error,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            agent_executor_kwargs={"handle_parsing_errors": True},
            prefix="You have already been provided with a dataframe df, all queries should be about that df. \
                Do not create dataframe. Do not read from any other sources. Do not use pd.read_clipboard. \
                If your response includes code, it will be executed, so you should define the code clearly. \
                Code in response will be split by \n so it should only include \n at the end of each line"
        )

        self.chain = self.prompt | self.agent
        self.history = ChatMessageHistory(session_id=self.session_id)
        self.agent_with_chat_history = RunnableWithMessageHistory(
            self.chain,
            lambda session_id: self.history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.file_name = file_name

        self.agent_with_trimmed_history = (
            RunnablePassthrough.assign(messages_trimmed=self.trim_messages)
            | self.agent_with_chat_history
        )

    def trim_messages(self, chain_input):
        # store the most recent 20 messages
        stored_messages = self.history.messages
        if len(stored_messages) <= 20:
            return False
        self.history.clear()
        for message in stored_messages[-20:]:
            self.history.add_message(message)
        return True

    def run(self, text):
        self.elem_queue.clear()
        self.execution_error.clear()

        result = self.agent_with_trimmed_history.with_config(
            configurable={"llm": "gpt4", "session_id": self.session_id}).invoke({"input": text})[
            'output']
        if self.model_name == LLMModel.GPT4o:
            result = self.agent_with_trimmed_history.with_config(
                configurable={"llm": "gpt4o", "session_id": self.session_id}).invoke({"input": text})[
                'output']
        if self.model_name == LLMModel.GPT4omini:
            result = self.agent_with_trimmed_history.with_config(
                configurable={"llm": "gpt4omini", "session_id": self.session_id}).invoke({"input": text})[
                'output']

         # Improve table removal logic
        table_pattern = r'(?s)\|.*?\|\n\|[-:]+\|\n(.*?)\n\n'
        result = re.sub(table_pattern, '', result)

        # Remove any remaining table-like structures
        result = re.sub(r'(?m)^\s*\|.*\|$', '', result)

        if (len(self.execution_error) > 0):
            result = f"""There was an error processing your request. Please provide a clearer query and try again.
                    (Error message: {str(self.execution_error[0])})"""
        if (len(self.elem_queue) > 0):
            return result, self.elem_queue
        else:
            return result, None

    def set_llm_model(self, model):
        self.model_name = model

    def _get_full_history(self) -> dict:
        return {
            "dataset": self.file_name if self.file_name is not None else 'unknown',
            "messages": messages_to_dict(self.history.messages)
        }

    def _get_agent_type(self, role) -> str:
        if role == 'human':
            return 'user'
        elif role == 'ai':
            return 'assistant'
        elif role == 'system-log':
            return 'system'
        return role

    def _get_simplified_history(self) -> dict:
        raw_history = self._get_full_history()
        history = []
        for message in raw_history['messages']:
            history.append({
                "role": self._get_agent_type(message['type']),
                "content": message['data']['content']
            })
        return {
            "dataset": raw_history['dataset'],
            "messages": history
        }

    def _get_text_history(self) -> str:
        raw_history = self._get_full_history()
        history = "DATASET: " + raw_history['dataset'] + '\n'
        history += "=" * 100 + '\n'
        for message in raw_history['messages']:
            history += self._get_agent_type(message['type']).upper(
            ) + ": " + message['data']['content'] + '\n'
        return history

    def get_history(self, c_format):
        if not isinstance(c_format, ConversationFormat):
            raise ValueError(
                f'Only {[v.value for v in ConversationFormat]} are allowed.')
        history = None
        extension = None
        if c_format == ConversationFormat.FULL_JSON:
            history = json.dumps(self._get_full_history())
            extension = '.json'
        elif c_format == ConversationFormat.SIMPLIFIED_JSON:
            history = json.dumps(self._get_simplified_history())
            extension = '.json'
        elif c_format == ConversationFormat.TEXT:
            history = self._get_text_history()
            extension = '.txt'
        if history is None:
            raise NotImplementedError("Unsupported format")
        return history, extension

    def persist_history(self, user_id,
                        persistence_type: PersistenceType = PersistenceType.DATABASE,
                        c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                        path: str = 'histories'):
        if not os.path.exists(path):
            os.makedirs(path)
        if persistence_type == PersistenceType.DATABASE and c_format == ConversationFormat.TEXT:
            raise TypeError(
                "Only JSON-like conversations can be written to the database")
        history, extension = self.get_history(c_format=c_format)
        if persistence_type == PersistenceType.FILE:
            with open(os.path.join(path, str(self.session_id) + extension), 'w') as f:
                f.write(history)
        elif (persistence_type == PersistenceType.DATABASE):
            Conversation.upsert(user_id, str(
                self.session_id), self.file_name, self.model_name, json.loads(history)['messages'])
        else:
            raise NotImplementedError("Unsupported persistence type")

    def system_log(self,
                   message,
                   persistence_type: PersistenceType = PersistenceType.DATABASE,
                   c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                   path: str = 'histories'):
        self.history.add_message(SystemLogMessage(content=message))
        self.persist_history(persistence_type=persistence_type,
                             c_format=c_format, path=path)
