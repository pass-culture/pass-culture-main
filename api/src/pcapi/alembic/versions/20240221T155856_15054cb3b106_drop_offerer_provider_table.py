"""
Drop Offerer Provider Table in favor of
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "15054cb3b106"
down_revision = "6d2971ccc616"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("unique_api_keys", "api_key", ["offererId", "providerId"])


def downgrade() -> None:
    op.drop_constraint("unique_api_keys", "api_key", type_="unique")
