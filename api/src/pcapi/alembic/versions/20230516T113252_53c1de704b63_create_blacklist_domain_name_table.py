"""create blacklist_domain_name table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "53c1de704b63"
down_revision = "ce6fe5bab319"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blacklisted_domain_name",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain"),
    )


def downgrade() -> None:
    op.drop_table("blacklisted_domain_name")
