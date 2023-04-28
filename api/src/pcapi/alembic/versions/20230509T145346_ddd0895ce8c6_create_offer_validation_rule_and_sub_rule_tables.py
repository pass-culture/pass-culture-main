"""Create "offer_validation_rule" and "offer_validation_sub_rule" tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ddd0895ce8c6"
down_revision = "b1ee65265887"
branch_labels = None
depends_on = None

OfferValidationModel = sa.Enum(
    "OFFER",
    "COLLECTIVE_OFFER",
    "COLLECTIVE_OFFER_TEMPLATE",
    "STOCK",
    "COLLECTIVE_STOCK",
    "VENUE",
    "OFFERER",
    name="offer_validation_model",
)
OfferValidationAttribute = sa.Enum(
    "CLASS_NAME",
    "NAME",
    "DESCRIPTION",
    "SIREN",
    "CATEGORY",
    "SUBCATEGORY_ID",
    "WITHDRAWAL_DETAILS",
    "MAX_PRICE",
    "PRICE",
    "PRICE_DETAIL",
    "SHOW_SUB_TYPE",
    name="offer_validation_attribute",
)

OfferValidationRuleOperator = sa.Enum(
    "EQUALS",
    "NOT_EQUALS",
    "GREATER_THAN",
    "GREATER_THAN_OR_EQUAL_TO",
    "LESS_THAN",
    "LESS_THAN_OR_EQUAL_TO",
    "IN",
    "NOT_IN",
    "CONTAINS",
    "CONTAINS_EXACTLY",
    name="offer_validation_rule_operator",
)


def upgrade() -> None:
    op.create_table(
        "offer_validation_rule",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("dateModified", sa.DateTime(), nullable=False),
        sa.Column("latestAuthorId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["latestAuthorId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "offer_validation_sub_rule",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("validationRuleId", sa.BigInteger(), nullable=False),
        sa.Column("model", OfferValidationModel, nullable=True),
        sa.Column("attribute", OfferValidationAttribute, nullable=False),
        sa.Column("operator", OfferValidationRuleOperator, nullable=False),
        sa.Column("comparated", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint(
            "(model IS NULL AND attribute = 'CLASS_NAME') OR (model IS NOT NULL AND attribute != 'CLASS_NAME')",
            name="check_not_model_and_attribute_class_or_vice_versa",
        ),
        sa.ForeignKeyConstraint(
            ["validationRuleId"],
            ["offer_validation_rule.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_offer_validation_sub_rule_validationRuleId"),
        "offer_validation_sub_rule",
        ["validationRuleId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_offer_validation_sub_rule_validationRuleId"), table_name="offer_validation_sub_rule")
    op.drop_table("offer_validation_sub_rule")
    op.drop_table("offer_validation_rule")
    OfferValidationModel.drop(op.get_bind())
    OfferValidationAttribute.drop(op.get_bind())
    OfferValidationRuleOperator.drop(op.get_bind())
