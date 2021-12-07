import dataclasses
import enum
import typing

from pcapi.core.users import models as users_models


@dataclasses.dataclass()
class SchoolType:
    id: str
    label: str

    def __init__(self, school_type: users_models.SchoolTypeEnum) -> None:
        self.id = school_type.name
        self.label = school_type.value
        super().__init__()


SCHOOL_TYPE_ID_ENUM = enum.Enum(
    "SchoolTypesIdEnum", {school_type.name: school_type.name for school_type in users_models.SchoolTypeEnum}
)
SCHOOL_TYPE_LABEL_ENUM = enum.Enum(
    "SchoolTypesLabelEnum", {school_type.name: school_type.value for school_type in users_models.SchoolTypeEnum}
)


@dataclasses.dataclass()
class Activity:
    id: str
    label: str
    associated_school_types_ids: typing.Optional[list[SCHOOL_TYPE_ID_ENUM]]

    def __init__(
        self,
        activity: users_models.ActivityEnum,
        associated_school_types_ids: typing.Optional[list[SCHOOL_TYPE_ID_ENUM]] = None,
    ) -> None:
        self.id = activity.name
        self.label = activity.value
        self.associated_school_types_ids = associated_school_types_ids or []
        super().__init__()


AGRICULTURAL_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.AGRICULTURAL_HIGH_SCHOOL)
APPRENTICE_FORMATION_CENTER = SchoolType(users_models.SchoolTypeEnum.APPRENTICE_FORMATION_CENTER)
MILITARY_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.MILITARY_HIGH_SCHOOL)
HOME_OR_REMOTE_SCHOOLING = SchoolType(users_models.SchoolTypeEnum.HOME_OR_REMOTE_SCHOOLING)
NAVAL_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.NAVAL_HIGH_SCHOOL)
PRIVATE_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PRIVATE_HIGH_SCHOOL)
PRIVATE_SECONDARY_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PRIVATE_SECONDARY_SCHOOL)
PUBLIC_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL)
PUBLIC_SECONDARY_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL)

ALL_SCHOOL_TYPES = [
    AGRICULTURAL_HIGH_SCHOOL,
    APPRENTICE_FORMATION_CENTER,
    MILITARY_HIGH_SCHOOL,
    HOME_OR_REMOTE_SCHOOLING,
    NAVAL_HIGH_SCHOOL,
    PRIVATE_HIGH_SCHOOL,
    PRIVATE_SECONDARY_SCHOOL,
    PUBLIC_HIGH_SCHOOL,
    PUBLIC_SECONDARY_SCHOOL,
]


MIDDLE_SCHOOL_STUDENT = Activity(
    users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT,
    [
        PRIVATE_SECONDARY_SCHOOL.id,
        PUBLIC_SECONDARY_SCHOOL.id,
        HOME_OR_REMOTE_SCHOOLING.id,
    ],
)
HIGH_SCHOOL_STUDENT = Activity(
    users_models.ActivityEnum.HIGH_SCHOOL_STUDENT,
    [
        AGRICULTURAL_HIGH_SCHOOL.id,
        MILITARY_HIGH_SCHOOL.id,
        NAVAL_HIGH_SCHOOL.id,
        PRIVATE_HIGH_SCHOOL.id,
        PUBLIC_HIGH_SCHOOL.id,
        HOME_OR_REMOTE_SCHOOLING.id,
        APPRENTICE_FORMATION_CENTER.id,
    ],
)
STUDENT = Activity(users_models.ActivityEnum.STUDENT)
EMPLOYEE = Activity(users_models.ActivityEnum.EMPLOYEE)
APPRENTICE = Activity(users_models.ActivityEnum.APPRENTICE)
APPRENTICE_STUDENT = Activity(users_models.ActivityEnum.APPRENTICE_STUDENT)
VOLUNTEER = Activity(users_models.ActivityEnum.VOLUNTEER)
INACTIVE = Activity(users_models.ActivityEnum.INACTIVE)
UNEMPLOYED = Activity(users_models.ActivityEnum.UNEMPLOYED)

ALL_ACTIVITIES = [
    MIDDLE_SCHOOL_STUDENT,
    HIGH_SCHOOL_STUDENT,
    STUDENT,
    EMPLOYEE,
    APPRENTICE,
    APPRENTICE_STUDENT,
    VOLUNTEER,
    INACTIVE,
    UNEMPLOYED,
]

SCHOOL_TYPE_ID_ENUM = enum.Enum(
    "SchoolTypesIdEnum", {school_type.name: school_type.name for school_type in users_models.SchoolTypeEnum}
)
SCHOOL_TYPE_LABEL_ENUM = enum.Enum(
    "SchoolTypesLabelEnum", {school_type.value: school_type.value for school_type in users_models.SchoolTypeEnum}
)
ACTIVITY_ID_ENUM = enum.Enum("ActivityIdEnum", {activity.id: activity.id for activity in ALL_ACTIVITIES})
ACTIVITY_LABEL_ENUM = enum.Enum("ActivityLabelEnum", {activity.label: activity.label for activity in ALL_ACTIVITIES})
