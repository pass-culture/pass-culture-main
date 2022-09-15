"""delete_profile_form_ff
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8b325869c549"
down_revision = "33ea40841a12"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_IN_PAGE_PROFILE_FORM",
        isActive=True,
        description="Active le formulaire d'édition de profile dans une page séparée",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
