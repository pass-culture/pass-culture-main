"""
remove_ff_WIP_FUTURE_OFFER
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e3e9ba056dab"
down_revision = "e199b0790783"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_FUTURE_OFFER",
        isActive=True,
        description="Activer la publication d'offres dans le futur",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
