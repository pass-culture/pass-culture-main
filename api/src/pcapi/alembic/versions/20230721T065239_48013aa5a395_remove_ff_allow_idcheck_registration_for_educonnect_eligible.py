"""
Remove ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "48013aa5a395"
down_revision = "2f2ddd4bf464"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE",
        isActive=True,
        description="Autoriser la redirection vers Ubble (en backup) pour les utilisateurs éligibles à éduconnect",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
