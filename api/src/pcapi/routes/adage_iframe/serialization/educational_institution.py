from pcapi.routes.serialization import BaseModel


class EducationalInstitutionWithBudgetResponseModel(BaseModel):
    id: int
    name: str
    institutionType: str
    postalCode: str
    city: str
    phoneNumber: str
    budget: int
