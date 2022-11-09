"""eac_image_columns
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a108c3bf5e27"
down_revision = "92484e2002ee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("imageCrop", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("collective_offer", sa.Column("imageCredit", sa.Text(), nullable=True))
    op.add_column("collective_offer", sa.Column("imageHasOriginal", sa.Boolean(), nullable=True))
    op.add_column(
        "collective_offer_template", sa.Column("imageCrop", postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column("collective_offer_template", sa.Column("imageCredit", sa.Text(), nullable=True))
    op.add_column("collective_offer_template", sa.Column("imageHasOriginal", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer_template", "imageHasOriginal")
    op.drop_column("collective_offer_template", "imageCredit")
    op.drop_column("collective_offer_template", "imageCrop")
    op.drop_column("collective_offer", "imageHasOriginal")
    op.drop_column("collective_offer", "imageCredit")
    op.drop_column("collective_offer", "imageCrop")
