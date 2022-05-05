"""Enable native id check version

Revision ID: 58df8264fe50
Revises: c2e2425fbac6
Create Date: 2021-05-06 15:14:21.619714

"""
from pcapi.models import Model


# revision identifiers, used by Alembic.
revision = "58df8264fe50"
down_revision = "c2e2425fbac6"
branch_labels = None
depends_on = None


def get_flag() -> Model:
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NATIVE_ID_CHECK_VERSION",
        isActive=True,
        description="Utilise la version d'ID-Check intégrée à l'application native",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())
