"""offerer_provider : table creation (step 1 of 6)
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "298d82d25d41"
down_revision = "4bec5e4e7ee7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offerer_provider",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=False),
        sa.Column("providerId", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("provider", sa.Column("logoUrl", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("provider", "logoUrl")
    op.drop_table("offerer_provider")
