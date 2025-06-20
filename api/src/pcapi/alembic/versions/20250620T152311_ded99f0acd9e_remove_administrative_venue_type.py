"""Remove administrative from venue type"""

from alembic import op

from pcapi.core import search
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ded99f0acd9e"
down_revision = "62d5ff24ee22"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    venue_query = db.session.query(offerers_models.Venue).filter(
        offerers_models.Venue.venueTypeCode == "ADMINISTRATIVE"
    )
    venue_ids = list(venue_query.with_entities(offerers_models.Venue.id).all())
    op.execute("""UPDATE venue SET venueTypeCode = 'OTHER' WHERE venueTypeCode = 'ADMINISTRATIVE';""")
    op.execute("""COMMIT;""")
    search.async_index_venue_ids(
        venue_ids,
        reason=search.IndexationReason.VENUE_UPDATE,
    )


def downgrade() -> None:
    pass
