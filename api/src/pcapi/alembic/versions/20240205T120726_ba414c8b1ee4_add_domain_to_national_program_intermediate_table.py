"""add domain to national program intermediate table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ba414c8b1ee4"
down_revision = "d118574a7888"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domain_to_national_program",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("domainId", sa.BigInteger(), nullable=False),
        sa.Column("nationalProgramId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["domainId"], ["educational_domain.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["nationalProgramId"], ["national_program.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domainId", "nationalProgramId", name="unique_domain_to_national_program"),
    )
    op.create_index(
        op.f("ix_domain_to_national_program_domainId"), "domain_to_national_program", ["domainId"], unique=False
    )
    op.create_index(
        op.f("ix_domain_to_national_program_nationalProgramId"),
        "domain_to_national_program",
        ["nationalProgramId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("domain_to_national_program")
