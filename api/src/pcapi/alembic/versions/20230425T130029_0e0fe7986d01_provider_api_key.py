"""provider_api_key: add provider_id column (1/3)
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0e0fe7986d01"
down_revision = "9fd9564814c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("api_key", sa.Column("providerId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "api_key_providerId_fkey",
        "api_key",
        "provider",
        ["providerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("api_key_providerId_fkey", "api_key", type_="foreignkey")
    op.drop_column("api_key", "providerId")
