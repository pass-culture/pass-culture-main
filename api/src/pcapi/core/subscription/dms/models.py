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


@dataclass
class DmsFieldErrorDetails:
    key: DmsFieldErrorKeyEnum
    value: str | None

    def get_field_label(self) -> str:
        return FIELD_LABEL.get(self.key, self.key.value)
