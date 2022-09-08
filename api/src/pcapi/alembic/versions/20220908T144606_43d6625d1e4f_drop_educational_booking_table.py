"""drop_educational_booking_table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "43d6625d1e4f"
down_revision = "1b778d61f672"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_educational_booking_educationalRedactorId", table_name="educational_booking")
    op.drop_index("ix_educational_booking_educationalYear_and_institution", table_name="educational_booking")
    op.drop_index("ix_booking_educationalBookingId", table_name="booking")
    op.drop_constraint("booking_educationalBookingId_fkey", "booking", type_="foreignkey")
    op.drop_column("booking", "educationalBookingId")
    op.drop_table("educational_booking")
    op.execute("DROP TYPE educationalbookingstatus")


def downgrade() -> None:
    op.create_table(
        "educational_booking",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("educationalInstitutionId", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("educationalYearId", sa.VARCHAR(length=30), autoincrement=False, nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("REFUSED", "USED_BY_INSTITUTE", name="educationalbookingstatus"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("confirmationDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("confirmationLimitDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("educationalRedactorId", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["educationalInstitutionId"],
            ["educational_institution.id"],
            name="educational_booking_educationalInstitutionId_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["educationalRedactorId"],
            ["educational_redactor.id"],
            name="educational_booking_educationalRedactorId_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["educationalYearId"], ["educational_year.adageId"], name="educational_booking_educationalYearId_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="educational_booking_pkey"),
    )
    op.add_column("booking", sa.Column("educationalBookingId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key(
        "booking_educationalBookingId_fkey", "booking", "educational_booking", ["educationalBookingId"], ["id"]
    )
    op.create_index("ix_booking_educationalBookingId", "booking", ["educationalBookingId"], unique=False)
    op.create_index(
        "ix_educational_booking_educationalYear_and_institution",
        "educational_booking",
        ["educationalInstitutionId", "educationalYearId"],
        unique=False,
    )
    op.create_index(
        "ix_educational_booking_educationalRedactorId", "educational_booking", ["educationalRedactorId"], unique=False
    )
