"""create_eac_refund_table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5e23156047b5"
down_revision = "66c2977b3cfe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collective_refund",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("ticket", sa.String(length=10), nullable=False),
        sa.Column("ministry", postgresql.ENUM(name="ministry", create_type=False), nullable=False),
        sa.Column("educationalInstitutionId", sa.BigInteger(), nullable=False),
        sa.Column("educationalYearId", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["educationalInstitutionId"],
            ["educational_institution.id"],
        ),
        sa.ForeignKeyConstraint(
            ["educationalYearId"],
            ["educational_year.adageId"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("collective_refund")
