"""add_business_unit_status_column"""
from alembic import op
import sqlalchemy as sa

import pcapi.core.finance.models as finance_models
import pcapi.utils.db as db_utils


revision = "d8d88115998e"
down_revision = "4e61b6f62735"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "business_unit",
        sa.Column(
            "status",
            db_utils.MagicEnum(finance_models.BusinessUnitStatus),
            nullable=False,
            server_default=finance_models.BusinessUnitStatus.ACTIVE.value,
        ),
    )


def downgrade():
    op.drop_column("business_unit", "status")
