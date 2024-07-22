from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages.base import messages_to_dict
import os
import time
from enum import Enum
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import ConfigurableField
from models.conversation import Conversation
from models.system_log import SystemLogMessage
import matplotlib
matplotlib.use('Agg')

class ConversationFormat(str, Enum):
    FULL_JSON = 'Full JSON'
    SIMPLIFIED_JSON = 'Simplified JSON'
    TEXT = 'Text'


class PersistenceType(str, Enum):
    DATABASE = 'Database'
    FILE = 'File'


class LLMModel(str, Enum):
    GPT4O = 'gpt4o'
    GPT4 = 'gpt4'
    GPT3DOT5 = 'gpt3dot5'


class DatasetAgent:
    def __init__(self, df, llm=None, file_name=None):
        if llm is None:
            self.llm = ChatOpenAI(temperature=0, model="gpt-4o").configurable_alternatives(
                ConfigurableField(id="llm"),
                default_key="gpt-4o",
                gpt3dot5=ChatOpenAI(model="gpt-3.5-turbo"),
                gpt4=ChatOpenAI(model="gpt-4-turbo"),
                gpt4o=ChatOpenAI(model="gpt-4o"),
            )
        else:
            self.llm = llm
        self.model_name = "gpt4o"
        self.session_id = round(time.time() * 1000)
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
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
            agent_executor_kwargs={"handle_parsing_errors": True}
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
        if self.model_name == LLMModel.GPT4O:
            return \
                self.agent_with_trimmed_history.with_config(
                    configurable={"llm": "gpt4o", "session_id": self.session_id}).invoke({"input": text})[
                    'output']
        elif self.model_name == LLMModel.GPT3DOT5:
            return \
                self.agent_with_trimmed_history.with_config(
                    configurable={"llm": "gpt3dot5", "session_id": self.session_id}).invoke({"input": text})[
                    'output']
        else:
            return \
                self.agent_with_trimmed_history.with_config(
                    configurable={"llm": "gpt4", "session_id": self.session_id}).invoke({"input": text})[
                    'output']

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
            history += self._get_agent_type(message['type']).upper() + ": " + message['data']['content'] + '\n'
        return history

    def get_history(self, c_format):
        if not isinstance(c_format, ConversationFormat):
            raise ValueError(f'Only {[v.value for v in ConversationFormat]} are allowed.')
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

    def persist_history(self,
                        persistence_type: PersistenceType = PersistenceType.DATABASE,
                        c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                        path: str = 'histories'):
        if not os.path.exists(path):
            os.makedirs(path)
        if persistence_type == PersistenceType.DATABASE and c_format == ConversationFormat.TEXT:
            raise TypeError("Only JSON-like conversations can be written to the database")
        history, extension = self.get_history(c_format=c_format)
        if persistence_type == PersistenceType.FILE:
            with open(os.path.join(path, str(self.session_id) + extension), 'w') as f:
                f.write(history)
        elif persistence_type == PersistenceType.DATABASE:
            Conversation.upsert(str(self.session_id), str(self.session_id), self.file_name, self.model_name,
                                json.loads(history)['messages'])
        else:
            raise NotImplementedError("Unsupported persistence type")

    def system_log(self,
                   message,
                   persistence_type: PersistenceType = PersistenceType.DATABASE,
                   c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                   path: str = 'histories'):
        self.history.add_message(SystemLogMessage(content=message))
        self.persist_history(persistence_type=persistence_type, c_format=c_format, path=path)
