from pcapi.routes.native.v1.serialization import BaseModel


class MailingContactResponseModel(BaseModel):
    pass


class MailingContactBodyModel(BaseModel):
    email: str
    dateOfBirth: str
    departmentCode: str
