"""Remove USE_INSEE_SIRENE_API FF"""
# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d2efd7e450c8"
down_revision = "4d76e0cf1691"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="USE_INSEE_SIRENE_API",
        isActive=True,
        description="tiliser la nouvelle API Sirene de l'Insee",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
