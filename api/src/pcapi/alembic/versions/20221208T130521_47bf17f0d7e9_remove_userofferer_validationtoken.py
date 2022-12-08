"""Remove_UserOfferer_validationToken
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "47bf17f0d7e9"
down_revision = "3e01ce2e72df"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("user_offerer_validationToken_key", "user_offerer", type_="unique")
    op.drop_column("user_offerer", "validationToken")


def downgrade() -> None:
    op.add_column(
        "user_offerer", sa.Column("validationToken", sa.VARCHAR(length=27), autoincrement=False, nullable=True)
    )
    op.create_unique_constraint("user_offerer_validationToken_key", "user_offerer", ["validationToken"])
