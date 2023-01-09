"""remove_FF_OFFER_FORM_V3
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1c46cd3b225f"
down_revision = "93551ad5b84c"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="OFFER_FORM_V3",
        isActive=True,
        description="Afficher la version 3 du formulaire d'offre",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
