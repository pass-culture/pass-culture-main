"""Remove USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS feature flag."""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ad44235c316b"
down_revision = "ba38f011683b"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS",
        isActive=True,
        description="Utilise le modèle VenueReimbursementPointLink pour les cashflows",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
