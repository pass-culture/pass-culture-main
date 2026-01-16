"""Rename Settlement constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a445ed1268d8"
down_revision = "ca1e0efa8036"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE settlement RENAME CONSTRAINT unique_cegid_settlement_id_bank_account_id TO unique_external_settlement_id_bank_account_id"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE settlement RENAME CONSTRAINT unique_external_settlement_id_bank_account_id TO unique_cegid_settlement_id_bank_account_id"
    )
