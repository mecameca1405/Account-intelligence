from pydantic import BaseModel
from ..clients.llm_client import LLMClient

class TestSchema(BaseModel):
    message: str

llm = LLMClient()

result = llm.generate_structured_output(
    prompt="Return a JSON with a field called message saying hello.",
    output_schema=TestSchema
)

print(result)