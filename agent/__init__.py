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
from utils.conversation import Conversation
from utils.system_log import SystemLogMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

class ConversationFormat(str, Enum):
    FULL_JSON = 'Full JSON'
    SIMPLIFIED_JSON = 'Simplified JSON'
    TEXT = 'Text'


class PersistenceType(str, Enum):
    DATABASE = 'Database'
    FILE = 'File'


class DatasetAgent:
    def __init__(self, df, llm=None, file_name=None):
        if llm is None:
            llm = ChatOpenAI(temperature=0, model="gpt-4o-2024-05-13")
        self.model_name = llm.model_name
        self.session_id = round(time.time() * 1000)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert in data science and machine learning especially in dealing with dataset bias issues. "
                    "Answer all questions to the best of your ability and give as more details as you can and think step by step."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        self.agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
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
        return \
        self.agent_with_trimmed_history.invoke({"input": text}, config={"configurable": {"session_id": self.session_id}})[
            'output']

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
