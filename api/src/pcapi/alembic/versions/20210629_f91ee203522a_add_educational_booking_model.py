"""add_educational_booking_model

Revision ID: f91ee203522a
Revises: 3c46248f7143
Create Date: 2021-06-29 10:43:18.269044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f91ee203522a"
down_revision = "3c46248f7143"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "educational_booking",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalInstitutionId", sa.BigInteger(), nullable=False),
        sa.Column("educationalYearId", sa.String(30), nullable=False),
        sa.Column("status", sa.Enum("REFUSED", "USED_BY_INSTITUTE", name="educationalbookingstatus"), nullable=True),
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
    op.create_index(
        op.f("ix_educational_booking_educationalYear_and_institution"),
        "educational_booking",
        ["educationalInstitutionId", "educationalYearId"],
        unique=False,
    )
    op.execute("CREATE TYPE booking_status AS ENUM ('PENDING', 'CONFIRMED', 'USED', 'CANCELLED')")
    op.add_column("booking", sa.Column("educationalBookingId", sa.BigInteger(), nullable=True))
    op.create_unique_constraint(None, "booking", ["educationalBookingId"])
    op.add_column(
        "booking",
        sa.Column("status", sa.Enum("PENDING", "CONFIRMED", "USED", "CANCELLED", name="booking_status"), nullable=True),
    )
    op.create_foreign_key(None, "booking", "educational_booking", ["educationalBookingId"], ["id"])


def downgrade() -> None:
    op.drop_column("booking", "status")
    op.drop_column("booking", "educationalBookingId")
    op.drop_index(op.f("ix_educational_booking_educationalYear_and_institution"), table_name="educational_booking")
    op.execute("DROP TYPE booking_status")
    op.drop_table("educational_booking")
    op.execute("DROP TYPE educationalbookingstatus")
