"""Drop bic column of BankAccount"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7ad93a37b8f0"
down_revision = "c3f894006573"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("bank_account", "bic")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column("bank_account", sa.Column("bic", sa.VARCHAR(length=11), autoincrement=False, nullable=True))
