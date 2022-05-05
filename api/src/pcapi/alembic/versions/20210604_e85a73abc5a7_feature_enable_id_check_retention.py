"""Add ENABLE_ID_CHECK_RETENTION feature flag

Revision ID: e85a73abc5a7
Revises: a3a703bc054b
Create Date: 2021-06-04 08:00:13.749757

"""
from pcapi.models import Model


# revision identifiers, used by Alembic.
revision = "e85a73abc5a7"
down_revision = "a3a703bc054b"
branch_labels = None
depends_on = None


def get_flag() -> Model:
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_ID_CHECK_RETENTION",
        isActive=True,
        description="Active le mode bassin de retention dans Id Check V2",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())
