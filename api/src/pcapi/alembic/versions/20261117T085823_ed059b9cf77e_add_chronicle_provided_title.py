"""Add "providedTitle" column and its check constraint to "chronicle" table, and make "productIdentifier" nullable"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ed059b9cf77e"
down_revision = "5206cabe15a3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("chronicle", "productIdentifier", existing_type=sa.Text(), nullable=True)
    op.add_column("chronicle", sa.Column("providedTitle", sa.Text(), nullable=True))
    op.create_check_constraint(
        "check_has_product_identifier_or_provided_title",
        "chronicle",
        '("productIdentifier" IS NOT NULL) OR ("providedTitle" IS NOT NULL)',
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("check_has_product_identifier_or_provided_title", "chronicle", type_="check")
    op.drop_column("chronicle", "providedTitle")
