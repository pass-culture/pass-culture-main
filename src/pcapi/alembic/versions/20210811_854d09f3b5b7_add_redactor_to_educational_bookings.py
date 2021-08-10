"""add_redactor_to_educational_bookings

Revision ID: 854d09f3b5b7
Revises: e910e1cc2112
Create Date: 2021-08-11 08:37:34.724421

"""
from alembic import op
import sqlalchemy as sa


revision = "854d09f3b5b7"
down_revision = "e910e1cc2112"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "educational_redactor",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("firstName", sa.String(length=128), nullable=False),
        sa.Column("lastName", sa.String(length=128), nullable=False),
        sa.Column("civility", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_educational_redactor_email"), "educational_redactor", ["email"], unique=True)
    op.add_column("educational_booking", sa.Column("educationalRedactorId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_educational_booking_educationalRedactorId"),
        "educational_booking",
        ["educationalRedactorId"],
    )
    op.create_foreign_key(None, "educational_booking", "educational_redactor", ["educationalRedactorId"], ["id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_educational_booking_educationalRedactorId"), table_name="educational_booking")
    op.drop_column("educational_booking", "educationalRedactorId")
    op.drop_index(op.f("ix_educational_redactor_email"), table_name="educational_redactor")
    op.drop_table("educational_redactor")
