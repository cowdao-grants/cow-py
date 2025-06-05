from pydantic import BaseModel as PyDanticBaseModel


class BaseModel(PyDanticBaseModel):
    model_config = {"populate_by_name": True}
