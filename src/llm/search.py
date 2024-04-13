import typing as T

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import PromptTemplate
from langchain_community.utils.openai_functions import convert_pydantic_to_openai_function
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from openai import OpenAI

from llm.utils import calculate_tokens


class OpenAiSearch:
    MODEL = "gpt-3.5-turbo-0125"

    def __init__(self, api_key: str, verbose: bool = False):
        self.parser = JsonOutputFunctionsParser()
        self.api_key = api_key
        self.verbose = verbose

    def search(
        self,
        inputs: T.Dict[str, str],
        prompt: PromptTemplate,
        model_function: type[BaseModel],
    ) -> T.Dict[str, str]:
        model = ChatOpenAI(api_key=self.api_key, temperature=0, model=self.MODEL)

        openai_functions = [convert_pydantic_to_openai_function(model_function)]

        chain = prompt | model.bind(functions=openai_functions) | self.parser
        output = chain.invoke(inputs)

        if self.verbose:
            print(output)

        if not output:
            raise ValueError("No output was generated")

        return output

    def calculate_tokens(
        self, inputs: T.Dict[str, str], output: T.Dict[str, str]
    ) -> T.Tuple[int, int, int]:
        input_tokens, output_tokens, total_tokens = calculate_tokens(inputs, output)

        if self.verbose:
            print(f"Input Tokens: {input_tokens}")
            print(f"Output Tokens: {output_tokens}")
            print(f"Total Tokens: {total_tokens}")

        return input_tokens, output_tokens, total_tokens
