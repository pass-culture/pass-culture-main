"""delete_collective_offer_choice_creation_ff
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "51d8855b12f6"
down_revision = "4e9a6643eeed"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION",
        isActive=True,
        description="Active l'écran carrefour sur la page de choix du type d’offre à créer, afin de pouvoir créer une offre collective vitrine dès le départ",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
