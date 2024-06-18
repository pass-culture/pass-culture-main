"""Delete unused Api Adresse FF
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cbd967876cbb"
down_revision = "f604375b4333"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_API_ADRESSE_WHILE_CREATING_UPDATING_VENUE",
        isActive=False,
        description="Activer les appels à l'API Adresse lors de création et modification des lieux",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
