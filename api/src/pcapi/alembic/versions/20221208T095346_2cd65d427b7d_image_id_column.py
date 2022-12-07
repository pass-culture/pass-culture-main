"""add imageId column for image management mixin
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2cd65d427b7d"
down_revision = "9f7d2f05b501"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("imageId", sa.Text(), nullable=True))
    op.add_column("collective_offer_template", sa.Column("imageId", sa.Text(), nullable=True))
    # done in migration to avoid dontime.
    # these table are very small (and very few of them have images)
    op.execute('UPDATE collective_offer SET "imageId"=id::text WHERE "imageCrop" is not NULL')
    op.execute('UPDATE collective_offer_template SET "imageId"=id::text WHERE "imageCrop" is not NULL')


def downgrade() -> None:
    op.drop_column("collective_offer_template", "imageId")
    op.drop_column("collective_offer", "imageId")
