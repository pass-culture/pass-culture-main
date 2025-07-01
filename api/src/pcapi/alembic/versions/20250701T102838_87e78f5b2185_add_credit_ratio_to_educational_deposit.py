"""Add creditRatio to educational_deposit"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "87e78f5b2185"
down_revision = "e294d51b08df"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("educational_deposit", sa.Column("creditRatio", sa.Numeric(precision=10, scale=3), nullable=True))
    op.create_check_constraint(
        constraint_name="check_credit_ratio_is_a_percentage",
        table_name="educational_deposit",
        condition='"creditRatio" IS NULL OR ("creditRatio" BETWEEN 0 AND 1)',
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="check_credit_ratio_is_a_percentage",
        table_name="educational_deposit",
        type_="check",
    )
    op.drop_column("educational_deposit", "creditRatio")
