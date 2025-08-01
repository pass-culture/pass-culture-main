"""Add video columns in OfferMetaData"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ecc93a7cd1a2"
down_revision = "0ed381176cbd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offer_meta_data", sa.Column("videoDuration", sa.BIGINT(), nullable=True))
    op.add_column("offer_meta_data", sa.Column("videoExternalId", sa.Text(), nullable=True))
    op.add_column("offer_meta_data", sa.Column("videoThumbnailUrl", sa.Text(), nullable=True))
    op.add_column("offer_meta_data", sa.Column("videoTitle", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("offer_meta_data", "videoDuration")
    op.drop_column("offer_meta_data", "videoExternalId")
    op.drop_column("offer_meta_data", "videoThumbnailUrl")
    op.drop_column("offer_meta_data", "videoTitle")
