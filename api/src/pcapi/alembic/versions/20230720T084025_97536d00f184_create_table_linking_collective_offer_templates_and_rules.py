"""Create table to link collective offer templates to the rules that flagged them
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "97536d00f184"
down_revision = "ffa31f343cba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "validation_rule_collective_offer_template_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ruleId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferTemplateId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["collectiveOfferTemplateId"], ["collective_offer_template.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ruleId"], ["offer_validation_rule.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("validation_rule_collective_offer_template_link")
