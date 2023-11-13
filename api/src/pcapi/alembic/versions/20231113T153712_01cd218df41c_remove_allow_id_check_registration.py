"""Remove ALLOW_IDCHECK_REGISTRATION FF"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "01cd218df41c"
down_revision = "844c963920b6"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ALLOW_IDCHECK_REGISTRATION",
        isActive=True,
        description="Autoriser les utilisateurs de 18 ans à suivre le parcours d inscription ID Check",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
