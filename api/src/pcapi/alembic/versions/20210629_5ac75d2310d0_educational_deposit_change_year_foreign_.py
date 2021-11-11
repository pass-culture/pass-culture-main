"""educational_deposit_change_year_foreign_key

Revision ID: 5ac75d2310d0
Revises: 9feb58815d16
Create Date: 2021-06-29 16:28:02.100009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ac75d2310d0"
down_revision = "9feb58815d16"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("educational_deposit", "educationalInstitutionId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_index("ix_educational_deposit_educationalYearId", table_name="educational_deposit")
    op.drop_column("educational_deposit", "educationalYearId")

    op.add_column("educational_deposit", sa.Column("educationalYearId", sa.String(length=30), nullable=False))
    op.create_index(
        op.f("ix_educational_deposit_educationalYearId"), "educational_deposit", ["educationalYearId"], unique=False
    )
    op.create_foreign_key(None, "educational_deposit", "educational_year", ["educationalYearId"], ["adageId"])


def downgrade() -> None:
    op.drop_index(op.f("ix_educational_deposit_educationalYearId"), table_name="educational_deposit")
    op.drop_column("educational_deposit", "educationalYearId")

    op.add_column(
        "educational_deposit", sa.Column("educationalYearId", sa.BIGINT(), autoincrement=False, nullable=True)
    )
    op.create_foreign_key(None, "educational_deposit", "educational_year", ["educationalYearId"], ["id"])
    op.create_index(
        "ix_educational_deposit_educationalYearId", "educational_deposit", ["educationalYearId"], unique=False
    )

    op.alter_column("educational_deposit", "educationalInstitutionId", existing_type=sa.BIGINT(), nullable=True)
