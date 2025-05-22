"""Create `collective_playlist` table"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.educational.models import PlaylistType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b429bc5435d6"
down_revision = "7894be402ca7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collective_playlist",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("type", MagicEnum(PlaylistType), nullable=False),
        sa.Column("distanceInKm", sa.Float(), nullable=True),
        sa.Column("institutionId", sa.BigInteger(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.Column("collectiveOfferTemplateId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["collectiveOfferTemplateId"],
            ["collective_offer_template.id"],
        ),
        sa.ForeignKeyConstraint(
            ["institutionId"],
            ["educational_institution.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_collective_playlist_collectiveOfferTemplateId"),
        "collective_playlist",
        ["collectiveOfferTemplateId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_collective_playlist_institutionId"), "collective_playlist", ["institutionId"], unique=False
    )
    op.create_index(op.f("ix_collective_playlist_venueId"), "collective_playlist", ["venueId"], unique=False)
    op.create_index(
        op.f("ix_collective_playlist_type_institutionId"),
        "collective_playlist",
        ["type", "institutionId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("collective_playlist")
