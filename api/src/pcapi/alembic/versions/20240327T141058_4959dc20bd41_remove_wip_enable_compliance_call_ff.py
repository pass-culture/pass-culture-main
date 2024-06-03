"""Remove WIP_ENABLE_COMPLIANCE_CALL Feature Flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4959dc20bd41"
down_revision = "c7d04bd67054"


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_COMPLIANCE_CALL",
        isActive=True,
        description="Activer les appels à l'API Compliance pour donner un score aux offres",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
