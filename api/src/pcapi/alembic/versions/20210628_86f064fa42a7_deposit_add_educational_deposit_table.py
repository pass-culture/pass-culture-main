"""deposit_add_educational_deposit_table

Revision ID: 86f064fa42a7
Revises: d49958abc723
Create Date: 2021-06-28 16:51:20.497989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "86f064fa42a7"
down_revision = "d49958abc723"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "educational_deposit",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalInstitutionId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["educationalInstitutionId"],
            ["educational_institution.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_educational_deposit_educationalInstitutionId"),
        "educational_deposit",
        ["educationalInstitutionId"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_educational_deposit_educationalInstitutionId"), table_name="educational_deposit")
    op.drop_table("educational_deposit")
