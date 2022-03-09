"""add_validation_type_to_offer
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f5a5da60e349"
down_revision = "22873a9e00e1"
branch_labels = None
depends_on = None


ValidationType = sa.Enum("AUTO", "MANUAL", name="validation_type")


def upgrade():
    ValidationType.create(op.get_bind(), checkfirst=True)
    op.add_column("collective_offer", sa.Column("lastValidationType", ValidationType, nullable=True))
    op.add_column("collective_offer_template", sa.Column("lastValidationType", ValidationType, nullable=True))
    op.add_column("offer", sa.Column("lastValidationType", ValidationType, nullable=True))


def downgrade():
    op.drop_column("offer", "lastValidationType")
    op.drop_column("collective_offer_template", "lastValidationType")
    op.drop_column("collective_offer", "lastValidationType")
    ValidationType.drop(op.get_bind())
