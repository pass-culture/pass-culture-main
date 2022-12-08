"""Remove_Offerer_validationToken
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3e01ce2e72df"
down_revision = "ad44235c316b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("offerer_validationToken_key", "offerer", type_="unique")
    op.drop_column("offerer", "validationToken")


def downgrade() -> None:
    op.add_column("offerer", sa.Column("validationToken", sa.VARCHAR(length=27), autoincrement=False, nullable=True))
    op.create_unique_constraint("offerer_validationToken_key", "offerer", ["validationToken"])
