"""make_contact_phone_optional_collective_offer
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "feba98cdb198"
down_revision = "fa7c663db77a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("collective_offer", "contactPhone", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("collective_offer_template", "contactPhone", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    op.alter_column("collective_offer_template", "contactPhone", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("collective_offer", "contactPhone", existing_type=sa.TEXT(), nullable=False)
