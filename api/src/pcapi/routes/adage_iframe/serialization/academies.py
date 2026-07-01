from pydantic import RootModel


class AcademiesResponseModel(RootModel):
    root: list[str]
