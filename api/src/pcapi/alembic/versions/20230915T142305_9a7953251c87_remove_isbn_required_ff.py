"""delete unused ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION ff"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9a7953251c87"
down_revision = "c21c9c622d05"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION",
        isActive=False,
        description="Active le champ isbn obligatoire lors de la création d'offre de type LIVRE_EDITION",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
