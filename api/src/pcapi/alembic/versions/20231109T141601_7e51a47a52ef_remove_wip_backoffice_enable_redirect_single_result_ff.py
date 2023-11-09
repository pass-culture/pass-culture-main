"""Remove WIP_BACKOFFICE_ENABLE_REDIRECT_SINGLE_RESULT feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7e51a47a52ef"
down_revision = "24afb3d5f6af"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_BACKOFFICE_ENABLE_REDIRECT_SINGLE_RESULT",
        isActive=True,
        description="Backoffice : Afficher directement les détails lorsque la recherche ne renvoie qu'un seul résultat",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
