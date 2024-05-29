from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
import pandas as pd


class DatasetAgent:
    def __init__(self, df):
        self.agent = create_pandas_dataframe_agent(
            ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106"),
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            agent_executor_kwargs={"handle_parsing_errors": True}
        )

    def run(self, text):
        return self.agent.run(text)
