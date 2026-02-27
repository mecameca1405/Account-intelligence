from typing import Optional, Type
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from app.core.config import settings


class LLMClient:
    """
    Encapsulates Gemini LLM interaction.
    Supports both free-form generation and structured output.
    """

    def __init__(self):
        self.model_name = settings.GEMINI_LLM_MODEL

        self._llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2,
        )

    def generate_text(self, prompt: str) -> str:
        """
        Generate free-form text.
        """
        response = self._llm.invoke(prompt)
        return response.content

    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Type[BaseModel],
    ) -> BaseModel:
        """
        Generate structured output validated by Pydantic schema.
        """

        parser = PydanticOutputParser(pydantic_object=output_schema)

        formatted_prompt = PromptTemplate(
            template=prompt + "\n\n{format_instructions}",
            input_variables=[],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            },
        )

        final_prompt = formatted_prompt.format()

        response = self._llm.invoke(final_prompt)

        return parser.parse(response.content)