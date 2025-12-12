from functools import partial

from pydantic_core import PydanticCustomError


# raise this error in validation instead of ValueError to avoid 'Value error, ...' in the error message
PydanticError = partial(PydanticCustomError, "custom_type")
