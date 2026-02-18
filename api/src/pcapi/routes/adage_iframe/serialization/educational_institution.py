from pcapi.routes.serialization import HttpBodyModel


class EducationalInstitutionBudgetResponseModel(HttpBodyModel):
    budget: int
