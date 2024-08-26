from langchain_core.messages import BaseMessage
from typing import Literal, List

class SystemLogMessage(BaseMessage):
    """Message for system logging.
    """

    type: Literal["system-log"] = "system-log"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "messages"]
    
class AssistantLogMessage(BaseMessage):
    """Message for system logging.
    """

    type: Literal["assistant-command"] = "assistant-command"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "messages"]