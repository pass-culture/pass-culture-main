"""Remove ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE feature flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "844c963920b6"
down_revision = "6d79f740fe27"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE",
        isActive=True,
        description="Utiliser la nouvelle règle de détection d'utilisateur en doublon",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
