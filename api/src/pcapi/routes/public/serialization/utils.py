import enum


class StrEnum(str, enum.Enum):
    # StrEnum is needed so that swagger ui displays the enum values
    # see https://github.com/swagger-api/swagger-ui/issues/6906
    pass
