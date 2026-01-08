"""Rename Settlement constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1de744b084de"
down_revision = "776aaf4893d0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("unique_cegid_settlement_id_bank_account_id"), "settlement", type_="unique")
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint(
        "unique_external_settlement_id_bank_account_id", "settlement", ["externalSettlementId", "bankAccountId"]
    )


def downgrade() -> None:
    op.drop_constraint("unique_external_settlement_id_bank_account_id", "settlement", type_="unique")
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint(
        op.f("unique_cegid_settlement_id_bank_account_id"),
        "settlement",
        ["externalSettlementId", "bankAccountId"],
        postgresql_nulls_not_distinct=False,
    )
