from dataclasses import dataclass
import enum


class DmsFieldErrorKeyEnum(enum.Enum):
    birth_date = "birth_date"
    first_name = "first_name"
    id_piece_number = "id_piece_number"
    last_name = "last_name"
    postal_code = "postal_code"


FIELD_LABEL = {
    DmsFieldErrorKeyEnum.birth_date: "ta date de naissance",
    DmsFieldErrorKeyEnum.first_name: "ton prénom",
    DmsFieldErrorKeyEnum.id_piece_number: "ta pièce d'identité",
    DmsFieldErrorKeyEnum.last_name: "ton nom",
    DmsFieldErrorKeyEnum.postal_code: "ton code postal",
}

INSTRUCTOR_FIELD_LABEL = {
    DmsFieldErrorKeyEnum.birth_date: "La date de naissance",
    DmsFieldErrorKeyEnum.first_name: "Le prénom",
    DmsFieldErrorKeyEnum.id_piece_number: "Le numéro de la pièce d'identité",
    DmsFieldErrorKeyEnum.last_name: "Le nom",
    DmsFieldErrorKeyEnum.postal_code: "Le code postal",
}


@dataclass
class DmsFieldErrorDetails:
    key: DmsFieldErrorKeyEnum
    value: str | None

    def get_field_label(self) -> str:
        return FIELD_LABEL.get(self.key, self.key.value)

    def get_instructor_field_label(self) -> str:
        return INSTRUCTOR_FIELD_LABEL.get(self.key, self.key.value)
