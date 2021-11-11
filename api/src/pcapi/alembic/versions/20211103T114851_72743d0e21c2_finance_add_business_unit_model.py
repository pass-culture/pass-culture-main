"""finance_add_business_unit_model
"""
from alembic import op
import sqlalchemy as sa

import pcapi.core.finance.models as finance_models
import pcapi.utils.db as db_utils


# revision identifiers, used by Alembic.
revision = "72743d0e21c2"
down_revision = "a5f8cf0d75da"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_unit",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("siret", sa.String(length=14), nullable=True),
        sa.Column("bankAccountId", sa.BigInteger(), nullable=True),
        sa.Column("cashflowFrequency", db_utils.MagicEnum(finance_models.Frequency), nullable=False),
        sa.Column("invoiceFrequency", db_utils.MagicEnum(finance_models.Frequency), nullable=False),
        sa.ForeignKeyConstraint(
            ["bankAccountId"],
            ["bank_information.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("siret"),
    )
    op.create_index(op.f("ix_business_unit_bankAccountId"), "business_unit", ["bankAccountId"], unique=False)


def downgrade():
    op.drop_table("business_unit")
