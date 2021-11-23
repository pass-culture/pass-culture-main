from pydantic import BaseModel


class BankInformationsResponseModel(BaseModel):
    id: int
    iban: str
    siret: str

    class Config:
        orm_mode = True


class ListBankInformationsResponseModel(BaseModel):
    __root__: list[BankInformationsResponseModel]

    class Config:
        orm_mode = True
