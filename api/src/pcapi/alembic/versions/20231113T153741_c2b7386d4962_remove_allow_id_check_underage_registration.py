"""Remove ALLOW_IDCHECK_UNDERAGE_REGISTRATION FF"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c2b7386d4962"
down_revision = "01cd218df41c"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ALLOW_IDCHECK_UNDERAGE_REGISTRATION",
        isActive=True,
        description="Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
