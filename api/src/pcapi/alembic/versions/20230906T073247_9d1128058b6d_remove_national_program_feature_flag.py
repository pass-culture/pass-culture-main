"""
remove_national_program_feature_flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9d1128058b6d"
down_revision = "e51bb5f173dd"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NATIONAL_SYSTEM",
        isActive=False,
        description="Activer le dispositif national dans les offres collectives",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
