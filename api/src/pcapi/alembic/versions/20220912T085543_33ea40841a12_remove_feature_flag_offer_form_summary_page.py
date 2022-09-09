"""remove_feature_flag_offer-form-summary_page
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "33ea40841a12"
down_revision = "992529bd24e5"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="OFFER_FORM_SUMMARY_PAGE",
        isActive=True,
        description="Afficher la page de récapitulatif de l'offre dans le formulaire V2",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
