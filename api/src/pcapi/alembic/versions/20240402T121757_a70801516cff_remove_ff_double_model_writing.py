"""Remove FF WIP_ENABLE_DOUBLE_MODEL_WRITING
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a70801516cff"
down_revision = "305d650503ba"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_DOUBLE_MODEL_WRITING",
        isActive=True,
        description="Activer la double écriture des coordonnées bancaires",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
