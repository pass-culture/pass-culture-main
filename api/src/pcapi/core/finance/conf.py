from enum import Enum


# TODO(fseguin|dbaty, 2022-01-11): maybe merge with core.categories.subcategories.ReimbursementRuleChoices ?
class RuleGroups(Enum):
    STANDARD = dict(
        label="Barème général",
        position=1,
    )
    BOOK = dict(
        label="Barème livres",
        position=2,
    )
    NOT_REIMBURSED = dict(
        label="Barème non remboursé",
        position=3,
    )
    CUSTOM = dict(
        label="Barème dérogatoire",
        position=4,
    )
    DEPRECATED = dict(
        label="Barème désuet",
        position=5,
    )
