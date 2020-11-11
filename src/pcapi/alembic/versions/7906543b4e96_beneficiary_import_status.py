"""Create table BeneficiaryImportStatus

Revision ID: 7906543b4e96
Revises: 8388f49ba035
Create Date: 2019-07-17 07:49:02.562498

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey
from sqlalchemy import func

from pcapi.models import ImportStatus


revision = "7906543b4e96"
down_revision = "8388f49ba035"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "beneficiary_import",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("demarcheSimplifieeApplicationId", sa.BigInteger, unique=False, nullable=False),
        sa.Column("status", sa.Enum(ImportStatus), nullable=False),
        sa.Column("date", sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column("detail", sa.VARCHAR(255), nullable=True),
        sa.Column("beneficiaryId", sa.BigInteger, ForeignKey("user.id"), nullable=True),
    )

    op.execute(
        """
    INSERT INTO beneficiary_import("demarcheSimplifieeApplicationId", status, "beneficiaryId", date)
    SELECT "demarcheSimplifieeApplicationId", 'CREATED', id, "dateCreated"
    FROM "user"
    WHERE "demarcheSimplifieeApplicationId" IS NOT NULL
    ;
    """
    )

    op.drop_column("user", "demarcheSimplifieeApplicationId")


def downgrade():
    op.add_column("user", sa.Column("demarcheSimplifieeApplicationId", sa.BigInteger, nullable=True))

    op.execute(
        """
    UPDATE "user"
    SET "demarcheSimplifieeApplicationId" = beneficiary_import."demarcheSimplifieeApplicationId"
    FROM "beneficiary_import"
    WHERE
        status = 'CREATED'
        AND beneficiary_import."beneficiaryId" = "user".id
    ;
    """
    )

    op.drop_table("beneficiary_import")

    enum_values = ("DUPLICATE", "ERROR", "CREATED", "REJECTED")
    temporary_enum = sa.Enum(*enum_values, name="importstatus")
    temporary_enum.drop(op.get_bind(), checkfirst=False)
