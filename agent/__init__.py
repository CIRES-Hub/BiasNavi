from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages.base import messages_to_dict
import os
from enum import Enum
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate, HumanMessagePromptTemplate, \
    SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import ConfigurableField
from agent.utils import create_pandas_dataframe_agent
from db_models.system_log import SystemLogMessage, AssistantLogMessage
from langchain_core.messages import HumanMessage
import re
from langchain.output_parsers import PydanticOutputParser
from db_models.conversation import Conversation
from flask_login import current_user
from agent.parser import ResponseFormat
import base64
from mimetypes import guess_type


class ConversationFormat(str, Enum):
    FULL_JSON = 'Full JSON'
    SIMPLIFIED_JSON = 'Simplified JSON'
    TEXT = 'Text'


class PersistenceType(str, Enum):
    DATABASE = 'Database'
    FILE = 'File'


# Function to encode a local image into data URL
def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    # Default to png
    if mime_type is None:
        mime_type = 'image/png'

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"


# def pass_argument_next_questions_class(question1, question2):
#     class NextQuestionFormat(BaseModel):
#         response: str = Field(description="Answer to the user's query")
#         suggestion1: str = Field(description=question1)
#         suggestion2: str = Field(description=question2)
#     return NextQuestionFormat

class DatasetAgent:

    def __init__(self, df, conversation_session=None, llm=None, file_name=None, user_id=None):
        self.user_id = user_id
        if llm is None:
            llm = ChatOpenAI(temperature=0.7, model="gpt-4o").configurable_alternatives(
                ConfigurableField(id="llm"),
                default_key="gpt4o",
                gpt4omini=ChatOpenAI(model="gpt-4o-mini"),
            )
        self.llm = llm
        self.model_name = llm.model_name
        self.session_id = conversation_session
        self.elem_queue = []
        self.execution_error: list[Exception] = []
        self.list_commands: list[str] = []
        self.file_name = file_name
        self.current_stage = "Identify"

        self.parser = PydanticOutputParser(pydantic_object=ResponseFormat)
        multimodal_prompt = self.configure_multimodal_prompt()
        self.prompt = self.configure_chat_prompt()

        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            verbose=True,
            elem_queue=self.elem_queue,
            execution_error=self.execution_error,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            agent_executor_kwargs={"handle_parsing_errors": True},
            list_commands=self.list_commands,
            prefix=current_user.prefix_prompt,
        )

        self.chain = self.prompt | self.agent
        self.multimodal_chain = multimodal_prompt | self.llm

        self.chat_history = ChatMessageHistory(session_id=self.session_id)

        self.agent_with_chat_history = RunnableWithMessageHistory(
            self.chain,
            lambda session_id: self.chat_history,
            history_messages_key="chat_history",
        )

        self.multimodal_chain_with_history = RunnableWithMessageHistory(
            self.multimodal_chain,
            lambda session_id: self.chat_history,
            history_messages_key="chat_history",
        )

        self.agent_with_trimmed_history = (
                RunnablePassthrough.assign(messages_trimmed=self.trim_messages)
                | self.agent_with_chat_history
        )

    def update_agent_prompt(self):
        # invoked when the user changed their prompts or user profile.
        prompt = self.configure_chat_prompt()
        self.chain.first = prompt
        self.chat_history = self.agent_with_chat_history.get_session_history(self.session_id)
        self.agent_with_chat_history = RunnableWithMessageHistory(
            self.chain,
            lambda session_id: self.chat_history,
            history_messages_key="chat_history",
        )
        self.agent_with_trimmed_history = (
                RunnablePassthrough.assign(messages_trimmed=self.trim_messages)
                | self.agent_with_chat_history
        )

    def configure_multimodal_prompt(self):
        multimodal_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                 "You are a data scientist. Describe the image provided in detail and find some insights about bias. "
                 "If there are potential biases, tell the user the ways to mitigate these biases."),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    [
                        {
                            "type": "text",
                            "text": "{text}",
                        },
                        {
                            "type": "image_url",
                            "image_url": "{encoded_image_url}",
                        },
                    ],
                ),
            ]
        )
        return multimodal_prompt

    def configure_user_msg_prompt(self):
        user_prompt = PromptTemplate(
            template=""""The current stage of bias management is {stage}. Please answer the my question: {input} given the retrieved context ({context}). The 
            response should be tailored to my background: {background} and align with the {stage}. Ensure that your 
            answer is informative while understandable for me. To make your answer clearer and instructive, 
            you can include examples and step-by-step instructions appropriate for my background. """,
            input_variables=["input", "context", "stage"],
            partial_variables={"background": current_user.persona_prompt},
        )
        user_message_prompt = HumanMessagePromptTemplate(prompt=user_prompt)
        return user_message_prompt

    def configure_system_msg_prompt(self):
        pipeline_prompt = """
            The         
        """
        system_prompt = PromptTemplate(
            template="""          

                    {custom_system_prompt}
                    {format_instructions}
                    {question_prompt}          

                    """,
            partial_variables={"format_instructions": self.parser.get_format_instructions(),
                               "question_prompt": current_user.follow_up_questions_prompt_1,
                               "custom_system_prompt": current_user.system_prompt}
        )
        # system_prompt = PromptTemplate(
        #     template="""
        #     {custom_system_prompt}
        #     """,
        #     partial_variables={"custom_system_prompt": current_user.system_prompt}
        # )
        system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt)
        return system_message_prompt

    def configure_chat_prompt(self):
        system_message_prompt = self.configure_system_msg_prompt()
        user_message_prompt = self.configure_user_msg_prompt()
        prompt = ChatPromptTemplate.from_messages(
            [
                system_message_prompt,
                MessagesPlaceholder(variable_name="chat_history"),
                user_message_prompt
            ]
        )
        return prompt

    def trim_messages(self, trimmed_message):
        # store the most recent 30 messages
        stored_messages = self.chat_history.messages
        if len(stored_messages) <= 30:
            return False
        self.chat_history.clear()
        for message in stored_messages[-30:]:
            self.chat_history.add_message(message)
        return True

    def describe_image(self, query, image_data):
        # image_url = "./UI/assets/cat.jpg"
        # image_data = local_image_to_data_url(image_url)
        result = self.multimodal_chain_with_history.with_config(
            configurable={"session_id": self.session_id}).invoke({"text": query, "encoded_image_url": image_data})
        return result

    def run(self, text, stage, context=''):
        self.elem_queue.clear()
        self.execution_error.clear()
        self.list_commands.clear()

        if self.model_name == "gpt-4-turbo":
            result = self.agent_with_trimmed_history.with_config(
                configurable={"llm": "gpt4", "session_id": self.session_id}).invoke({"input": text, "stage": stage, "context": context})
        elif self.model_name == "gpt-4o-2024-08-06":
            result = self.agent_with_trimmed_history.with_config(
                configurable={"llm": "gpt4o", "session_id": self.session_id}).invoke({"input": text, "stage": stage, "context": context})
        else:
            result = self.agent_with_trimmed_history.with_config(
                configurable={"llm": "gpt4omini", "session_id": self.session_id}).invoke({"input": text, "stage": stage, "context": context})

        # Parse response 
        suggestions = []
        stage = ""
        try:
            result = self.parser.parse(result['output'])
            suggestions.append(result.question1)
            suggestions.append(result.question2)
            stage = result.stage
            operation = result.operation
            explanation = result.explanation
            result = result.answer
            if stage is not self.current_stage and stage in ["Identify", "Measure", "Surface", "Adapt"]:
                self.current_stage = stage
            else:
                stage = self.current_stage

        except Exception as e:
            # cannot be parsed in the above format, directly return the answer
            self.execution_error.append(e)
            result = result['output']
            return result, self.elem_queue, suggestions, stage, operation, explanation

        # Improve table removal logic
        table_pattern = r'(?s)\|.*?\|\n\|[-:]+\|\n(.*?)\n\n'
        result = re.sub(table_pattern, '', result)

        # Remove any remaining table-like structures
        result = re.sub(r'(?m)^\s*\|.*\|$', '', result)
        # if len(self.list_commands) > 0:
        #     self.persist_commands(json.dumps({"query": self.list_commands[0]}))
        if len(self.execution_error) > 0:
            result = f"""There was an error processing your request. Please provide a clearer query and try again.
                    (Error message: {str(self.execution_error[0])})"""
        if len(self.elem_queue) > 0:
            return result, self.elem_queue, suggestions, stage, operation, explanation
        else:
            return result, None, suggestions, stage, operation, explanation

    def set_llm_model(self, model):
        self.model_name = model

    def _get_full_history(self) -> dict:
        return {
            "dataset": self.file_name if self.file_name is not None else 'unknown',
            "messages": messages_to_dict(self.chat_history.messages)
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
        elif persistence_type == PersistenceType.DATABASE:
            Conversation.upsert(user_id, str(
                self.session_id), self.file_name, self.model_name, json.loads(history)['messages'])
        else:
            raise NotImplementedError("Unsupported persistence type")

    def system_log(self,
                   message,
                   persistence_type: PersistenceType = PersistenceType.DATABASE,
                   c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                   path: str = 'histories'):
        self.chat_history.add_message(SystemLogMessage(content=message))
        self.persist_history(persistence_type=persistence_type,
                             c_format=c_format, path=path)

    def add_user_action_to_history(self, message):
        self.chat_history.add_message(HumanMessage(content=message))

    def persist_commands(self,
                         message,
                         persistent_type: PersistenceType = PersistenceType.DATABASE,
                         c_format: ConversationFormat = ConversationFormat.SIMPLIFIED_JSON,
                         path: str = 'histories'):
        self.chat_history.add_message(AssistantLogMessage(content=message))

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
        elif persistent_type == PersistenceType.DATABASE:
            Conversation.upsert(str(current_user.id), str(
                self.session_id), self.file_name, self.model_name, json.loads(history)['messages'])
        else:
            raise NotImplementedError("Unsupported persistence type")
