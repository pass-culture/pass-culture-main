from pydantic import BaseModel


class BankInformationsResponseModel(BaseModel):
    bic: str
    id: int
    iban: str
    name: str
    siret: str

    class Config:
        orm_mode = True


class ListBankInformationsResponseModel(BaseModel):
    __root__: list[BankInformationsResponseModel]

    class Config:
        orm_mode = True
