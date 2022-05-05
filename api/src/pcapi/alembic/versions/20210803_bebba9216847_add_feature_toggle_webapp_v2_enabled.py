"""Add WEBAPP_V2_ENABLED feature flag

Revision ID: bebba9216847
Revises: ff887e7b4f89
Create Date: 2021-08-03 17:27:45.546319

"""
from pcapi.models import Model


# revision identifiers, used by Alembic.
revision = "bebba9216847"
down_revision = "ff887e7b4f89"
branch_labels = None
depends_on = None


def get_flag() -> Model:
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WEBAPP_V2_ENABLED",
        isActive=True,
        description="Utiliser la nouvelle web app (décli web/v2) au lieu de l'ancienne",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())
