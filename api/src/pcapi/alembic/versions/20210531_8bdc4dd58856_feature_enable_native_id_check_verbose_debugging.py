"""Add ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING feature flag

Revision ID: 8bdc4dd58856
Revises: e8199ef92975
Create Date: 2021-05-31 09:54:01.457723

"""
from pcapi.models import Model


# revision identifiers, used by Alembic.
revision = "8bdc4dd58856"
down_revision = "e8199ef92975"
branch_labels = None
depends_on = None


def get_flag() -> Model:
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING",
        isActive=False,
        description="Active le mode debug Firebase pour l'Id Check intégrée à l application native",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())
