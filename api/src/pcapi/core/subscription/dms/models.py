from dataclasses import dataclass
import enum
import typing


class DmsParsingErrorKeyEnum(enum.Enum):
    birth_date = "birth_date"
    first_name = "first_name"
    id_piece_number = "id_piece_number"
    last_name = "last_name"
    postal_code = "postal_code"


FIELD_LABEL = {
    DmsParsingErrorKeyEnum.birth_date: "ta date de naissance",
    DmsParsingErrorKeyEnum.first_name: "ton prénom",
    DmsParsingErrorKeyEnum.id_piece_number: "ta pièce d'identité",
    DmsParsingErrorKeyEnum.last_name: "ton nom",
    DmsParsingErrorKeyEnum.postal_code: "ton code postal",
}


@dataclass
class DmsParsingErrorDetails:
    key: DmsParsingErrorKeyEnum
    value: typing.Optional[str]

    def get_field_label(self) -> str:
        return FIELD_LABEL.get(self.key, self.key.value)
