import enum


class StudentLevels(enum.Enum):
    ECOLES_MARSEILLE_MATERNELLE = "Écoles Marseille - Maternelle"
    ECOLES_MARSEILLE_CP_CE1_CE2 = "Écoles Marseille - CP, CE1, CE2"
    ECOLES_MARSEILLE_CM1_CM2 = "Écoles Marseille - CM1, CM2"
    COLLEGE6 = "Collège - 6e"
    COLLEGE5 = "Collège - 5e"
    COLLEGE4 = "Collège - 4e"
    COLLEGE3 = "Collège - 3e"
    CAP1 = "CAP - 1re année"
    CAP2 = "CAP - 2e année"
    GENERAL2 = "Lycée - Seconde"
    GENERAL1 = "Lycée - Première"
    GENERAL0 = "Lycée - Terminale"

    @classmethod
    def primary_levels(cls) -> set:
        return {
            cls.ECOLES_MARSEILLE_MATERNELLE,
            cls.ECOLES_MARSEILLE_CP_CE1_CE2,
            cls.ECOLES_MARSEILLE_CM1_CM2,
        }


class AdageFrontRoles(enum.Enum):
    REDACTOR = "redactor"
    READONLY = "readonly"


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"
