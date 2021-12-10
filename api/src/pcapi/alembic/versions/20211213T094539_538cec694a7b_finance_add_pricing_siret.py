"""Add Pricing.siret column + index"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "538cec694a7b"
down_revision = "854968b5a6c0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("pricing", sa.Column("siret", sa.String(length=14), nullable=False))
    op.create_index(op.f("ix_pricing_siret"), "pricing", ["siret"], unique=False)


def downgrade():
    op.drop_column("pricing", "siret")
