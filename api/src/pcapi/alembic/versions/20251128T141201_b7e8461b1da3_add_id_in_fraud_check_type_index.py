"""Add id in fraud check initiated index"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b7e8461b1da3"
down_revision = "ec069bb7efa0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION lock_timeout='300s'")
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            op.f("ix_beneficiary_fraud_check_type_initiated_status"),
            table_name="beneficiary_fraud_check",
            postgresql_where="((status = 'STARTED'::text) OR (status = 'PENDING'::text))",
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_beneficiary_fraud_check_type_initiated_status",
            "beneficiary_fraud_check",
            ["id", "type"],
            unique=False,
            postgresql_where=sa.text("status = 'STARTED' OR status = 'PENDING'"),
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION lock_timeout='300s'")
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_beneficiary_fraud_check_type_initiated_status",
            table_name="beneficiary_fraud_check",
            postgresql_where=sa.text("status = 'STARTED' OR status = 'PENDING'"),
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f("ix_beneficiary_fraud_check_type_initiated_status"),
            "beneficiary_fraud_check",
            ["type"],
            unique=False,
            postgresql_where="((status = 'STARTED'::text) OR (status = 'PENDING'::text))",
            if_not_exists=True,
            postgresql_concurrently=True,
        )
