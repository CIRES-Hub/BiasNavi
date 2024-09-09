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
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import ConfigurableField
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from agent.utils import create_pandas_dataframe_agent
from db_models.conversation import Conversation
from db_models.system_log import SystemLogMessage, AssistantLogMessage
import re
from langchain.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from flask_login import current_user


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

def pass_argument_next_questions_class(question1, question2): 
    class NextQuestionFormat(BaseModel):
        response: str = Field(description="Answer to the user's query")
        suggestion1: str = Field(description=question1)
        suggestion2: str = Field(description=question2)
    return NextQuestionFormat

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
        self.list_commands: list[str] = []
        self.parser = PydanticOutputParser(pydantic_object=pass_argument_next_questions_class(current_user.follow_up_questions_prompt_1, current_user.follow_up_questions_prompt_2))
        prompt = PromptTemplate(
            template="Answer the user's query: {input}"
            "{format_instructions}",
            input_variables=["input"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        user_prompt = HumanMessagePromptTemplate(prompt=prompt)
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    current_user.system_prompt
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                user_prompt
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
            list_commands=self.list_commands,
            prefix=current_user.prefix_prompt
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
        self.list_commands.clear()

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
        
        # Parse response 
        suggestions = []
        suggestions.append(self.parser.parse(result).suggestion1)
        suggestions.append(self.parser.parse(result).suggestion2)
        result = self.parser.parse(result).response
        
         # Improve table removal logic
        table_pattern = r'(?s)\|.*?\|\n\|[-:]+\|\n(.*?)\n\n'
        result = re.sub(table_pattern, '', result)

        # Remove any remaining table-like structures
        result = re.sub(r'(?m)^\s*\|.*\|$', '', result)
        if (len(self.list_commands) > 0):
            self.persist_commands(json.dumps({"query": self.list_commands[0]}))
        if (len(self.execution_error) > 0):
            result = f"""There was an error processing your request. Please provide a clearer query and try again.
                    (Error message: {str(self.execution_error[0])})"""
        if (len(self.elem_queue) > 0):
            return result, self.elem_queue, suggestions
        else:
            return result, None, suggestions

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
        elif role == 'assistant-command':
            return 'assistant-command'
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
    
    def persist_commands(self,
                         message,
                         persistent_type: PersistenceType = PersistenceType.DATABASE,
                         c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                         path: str = 'histories'):
        self.history.add_message(AssistantLogMessage(content=message))
        
        if not os.path.exists(path):
            os.makedirs(path)
        if persistent_type == PersistenceType.DATABASE and c_format == ConversationFormat.TEXT:
            raise TypeError(
                "Only JSON-like conversations can be written to the database")
            
        history = json.dumps(self._get_simplified_history())
        extension = '.json'
        
        if persistent_type == PersistenceType.FILE:
            with open(os.path.join(path, str(self.session_id) + extension), 'w') as f:
                f.write(history)
        elif (persistent_type == PersistenceType.DATABASE):
            Conversation.upsert(str(current_user.id), str(
                self.session_id), self.file_name, self.model_name, json.loads(history)['messages'])
        else:
            raise NotImplementedError("Unsupported persistence type")
