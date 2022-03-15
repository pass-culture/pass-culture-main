"""Remove PRO_ENABLE_UPLOAD_VENUE_IMAGE feature flag."""


# revision identifiers, used by Alembic.
revision = "0efdf36fd5d7"
down_revision = "d6c2ce466236"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="PRO_ENABLE_UPLOAD_VENUE_IMAGE",
        isActive=True,
        description="Active la fonctionnalité d'upload des images des lieux permanents",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
