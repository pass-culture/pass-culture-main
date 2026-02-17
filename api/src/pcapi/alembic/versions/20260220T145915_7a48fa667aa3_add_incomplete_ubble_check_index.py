"""Add incomplete ubble check index"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7a48fa667aa3"
down_revision = "01d229a2edb1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_beneficiary_fraud_check_incomplete_ubble",
            "beneficiary_fraud_check",
            ["id"],
            unique=False,
            postgresql_where=sa.text(
                "status = 'OK' AND type = 'UBBLE' AND \"eligibilityType\" = 'AGE17_18' AND (\"thirdPartyId\" LIKE 'idv_' || '%%') AND ((\"resultContent\" ->> 'birth_place') IS NULL OR (\"resultContent\" ->> 'document_issuing_country') IS NULL OR (\"resultContent\" ->> 'nationality') IS NULL)"
            ),
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_beneficiary_fraud_check_incomplete_ubble",
            table_name="beneficiary_fraud_check",
            postgresql_where=sa.text(
                "status = 'OK' AND type = 'UBBLE' AND \"eligibilityType\" = 'AGE17_18' AND (\"thirdPartyId\" LIKE 'idv_' || '%%') AND ((\"resultContent\" ->> 'birth_place') IS NULL OR (\"resultContent\" ->> 'document_issuing_country') IS NULL OR (\"resultContent\" ->> 'nationality') IS NULL)"
            ),
            if_exists=True,
            postgresql_concurrently=True,
        )
