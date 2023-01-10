"""Remove_VENUE_FORM_V2_feature_flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f94795ee981a"
down_revision = "525089ccbb4d"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="VENUE_FORM_V2",
        isActive=False,
        description="Afficher la version 2 du formulaire de lieu",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
