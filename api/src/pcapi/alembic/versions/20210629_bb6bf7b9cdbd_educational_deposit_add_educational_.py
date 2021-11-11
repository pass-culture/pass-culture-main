"""educational_deposit_add_educational_year_relationship

Revision ID: bb6bf7b9cdbd
Revises: f0cad4632e56
Create Date: 2021-06-29 08:27:03.121258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bb6bf7b9cdbd"
down_revision = "f0cad4632e56"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("educational_deposit", sa.Column("educationalYearId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_educational_deposit_educationalYearId"), "educational_deposit", ["educationalYearId"], unique=False
    )
    op.create_foreign_key(
        None,
        "educational_deposit",
        "educational_year",
        ["educationalYearId"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_educational_deposit_educationalYearId"), table_name="educational_deposit")
    op.drop_column("educational_deposit", "educationalYearId")
