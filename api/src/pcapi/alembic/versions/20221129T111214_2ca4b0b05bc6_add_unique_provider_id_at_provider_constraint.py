"""add unique_provider_id_at_provider constraint"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2ca4b0b05bc6"
down_revision = "d223c62b00b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "unique_provider_id_at_provider", "cinema_provider_pivot", ["providerId", "idAtProvider"]
    )


def downgrade() -> None:
    op.drop_constraint("unique_provider_id_at_provider", "cinema_provider_pivot", type_="unique")
