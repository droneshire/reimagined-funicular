import typing as T

from langchain_core.pydantic_v1 import BaseModel


def get_model_fields(model: BaseModel):
    fields = {}
    for field_name, field_info in model.__fields__.items():
        fields[field_name] = {
            "type": field_info.type_,
            "description": field_info.field_info.description,
        }
    return fields


def calculate_tokens(data: T.Dict[str, str], output: T.Dict[str, str]) -> T.Tuple[int, int, int]:
    input_tokens = sum(len(str(value).split()) for value in data.values())
    output_tokens = sum(len(str(value).split()) for value in output.values())
    total_tokens = input_tokens + output_tokens

    return input_tokens, output_tokens, total_tokens
