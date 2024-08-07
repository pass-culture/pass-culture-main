import dataclasses
import enum

from pcapi.core.users import models as users_models


@dataclasses.dataclass()
class SchoolType:
    id: str
    description: str | None
    label: str

    def __init__(self, school_type: users_models.SchoolTypeEnum, description: str | None = None) -> None:
        self.id = school_type.name
        self.description = description
        self.label = school_type.value
        super().__init__()


SchoolTypeIdEnum = enum.Enum(  # type: ignore[misc]
    "SchoolTypesIdEnum", {school_type.name: school_type.name for school_type in users_models.SchoolTypeEnum}
)
SchoolTypeValueEnum = enum.Enum(  # type: ignore[misc]
    "SchoolTypesValueEnum", {school_type.value: school_type.value for school_type in users_models.SchoolTypeEnum}
)


@dataclasses.dataclass()
class Activity:
    id: str
    label: str
    description: str | None

    def __init__(
        self,
        activity: users_models.ActivityEnum,
        description: str | None = None,
    ) -> None:
        self.id = activity.name
        self.label = activity.value
        self.description = description
        super().__init__()


AGRICULTURAL_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.AGRICULTURAL_HIGH_SCHOOL)
APPRENTICE_FORMATION_CENTER = SchoolType(users_models.SchoolTypeEnum.APPRENTICE_FORMATION_CENTER)
MILITARY_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.MILITARY_HIGH_SCHOOL)
HOME_OR_REMOTE_SCHOOLING = SchoolType(
    users_models.SchoolTypeEnum.HOME_OR_REMOTE_SCHOOLING, description="À domicile, CNED, institut de santé, etc."
)
NAVAL_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.NAVAL_HIGH_SCHOOL)
PRIVATE_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PRIVATE_HIGH_SCHOOL)
PRIVATE_SECONDARY_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PRIVATE_SECONDARY_SCHOOL)
PUBLIC_HIGH_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL)
PUBLIC_SECONDARY_SCHOOL = SchoolType(users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL)


MIDDLE_SCHOOL_STUDENT = Activity(users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT)
HIGH_SCHOOL_STUDENT = Activity(users_models.ActivityEnum.HIGH_SCHOOL_STUDENT)
STUDENT = Activity(users_models.ActivityEnum.STUDENT)
EMPLOYEE = Activity(users_models.ActivityEnum.EMPLOYEE)
APPRENTICE = Activity(users_models.ActivityEnum.APPRENTICE)
APPRENTICE_STUDENT = Activity(users_models.ActivityEnum.APPRENTICE_STUDENT)
VOLUNTEER = Activity(users_models.ActivityEnum.VOLUNTEER, description="En service civique")
INACTIVE = Activity(users_models.ActivityEnum.INACTIVE, description="En incapacité de travailler")
UNEMPLOYED = Activity(users_models.ActivityEnum.UNEMPLOYED, description="En recherche d'emploi")


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

ActivityIdEnum = enum.Enum("ActivityIdEnum", {activity.id: activity.id for activity in ALL_ACTIVITIES})  # type: ignore[misc]
ActivityValueEnum = enum.Enum("ActivityValueEnum", {activity.label: activity.label for activity in ALL_ACTIVITIES})  # type: ignore[misc]
