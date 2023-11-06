"""Add DeactivableMixin to OfferValidationRules and drop unused columns
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3ab07dc09e34"
down_revision = "ce93f52f9f59"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "offer_validation_rule", sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )
    op.drop_constraint("offer_validation_rule_latestAuthorId_fkey", "offer_validation_rule", type_="foreignkey")
    op.drop_column("offer_validation_rule", "latestAuthorId")
    op.drop_column("offer_validation_rule", "dateModified")


def downgrade() -> None:
    op.drop_column("offer_validation_rule", "isActive")
    op.add_column(
        "offer_validation_rule", sa.Column("dateModified", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
    )
    op.add_column("offer_validation_rule", sa.Column("latestAuthorId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key(
        "offer_validation_rule_latestAuthorId_fkey", "offer_validation_rule", "user", ["latestAuthorId"], ["id"]
    )
