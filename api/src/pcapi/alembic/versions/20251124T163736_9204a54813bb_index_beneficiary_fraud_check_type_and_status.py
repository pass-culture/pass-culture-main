"""Add index on eligibilityType field of BeneficiaryFraudCheck model with status in (started, pending)"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9204a54813bb"
down_revision = "b91453933c08"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_fraud_check_type_initiated_status",
            "beneficiary_fraud_check",
            ["eligibilityType"],
            postgresql_where=sa.text("status IN ('started', 'pending')"),
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_fraud_check_type_initiated_status",
            table_name="beneficiary_fraud_check",
            postgresql_concurrently=True,
            if_exists=True,
        )
