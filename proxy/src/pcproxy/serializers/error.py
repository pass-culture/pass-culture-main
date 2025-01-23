import pydantic


class SimpleError(pydantic.BaseModel):
    code: str
