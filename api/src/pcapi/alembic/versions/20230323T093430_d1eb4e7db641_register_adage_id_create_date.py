"""register_adage_id_create_date
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d1eb4e7db641"
down_revision = "a8c91c7a2a9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("adageInscriptionDate", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "adageInscriptionDate")
