from typing import Optional
from pydantic import BaseModel, Field


# Pydantic
class ResponseFormat(BaseModel):
    """Respond in a conversational manner."""
    answer: str = Field(description="The answer to the user's question")
    question1: str = Field(description="The first generated follow-up question based on the context.")
    question2: str = Field(description="The second generated follow-up question based on the context.")
    sensitive_attributes: list[str] = Field(description="The identfied sensitive attributes that may cause biased outcome.")
    stage: str = Field(description="The current stage of the bias management pipeline.")
    operation: str = Field(description="The next operation in the current bias management pipeline.")
    explanation: str = Field(description="Explain why this operation is recommended.")

# resp_format_as_dict = {
#     "name": "ResponseFormat",
#     "description": "Respond in a conversational manner to answer the user's question while generate two follow-up questions.",
#     "strict":True,
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "answer": {
#                 "description": "Answer",
#                 "type": "string"
#             },
#             "question1": {
#                 "description": "The first follow-up question",
#                 "type": "string"
#             },
#             "question2": {
#                 "description": "The second follow-up question",
#                 "type": "string"
#             }
#         },
#         "required": ["answer", "question1", "question2"],
#         "additionalProperties": False
#     }
# }

