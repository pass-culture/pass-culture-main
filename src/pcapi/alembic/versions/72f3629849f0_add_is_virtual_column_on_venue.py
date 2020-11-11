"""Add isVirtual column on Venue table. It represents whether the venue is digital.

Revision ID: 72f3629849f0
Revises: e2960d28528f
Create Date: 2018-08-10 08:16:46.210630

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression


revision = "72f3629849f0"
down_revision = "e2960d28528f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("isVirtual", sa.Boolean(), nullable=False, server_default=expression.false()))

    op.alter_column("venue", "address", existing_type=sa.VARCHAR(length=200), nullable=True)
    op.alter_column("venue", "postalCode", existing_type=sa.VARCHAR(length=6), nullable=True)
    op.alter_column("venue", "city", existing_type=sa.VARCHAR(length=50), nullable=True)
    op.alter_column("venue", "departementCode", existing_type=sa.VARCHAR(length=3), nullable=True)

    op.create_check_constraint(
        constraint_name="check_is_virtual_xor_has_address",
        table_name="venue",
        condition="""
            (
                "isVirtual" IS TRUE
                AND (address IS NULL AND "postalCode" IS NULL AND city IS NULL AND "departementCode" IS NULL)
            )
            OR
            (
                "isVirtual" IS FALSE
                AND (address IS NOT NULL AND "postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
            )
        """,
    )


def downgrade():
    pass
