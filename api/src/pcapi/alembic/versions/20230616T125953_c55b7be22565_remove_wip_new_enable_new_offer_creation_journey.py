"""FIXME: the comment below appears in the output of `alembic history`.
Remove this FIXME and make the comment below easily readable.

remove_wip_new_enable_new_offer_creation_journey
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c55b7be22565"
down_revision = "e84fda00f67c"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY",
        isActive=True,
        description="Nouveau parcours de creation d'offre optimisé",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
