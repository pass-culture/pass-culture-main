"""Remove ENABLE_IDCHECK_FRAUD_CONTROLS feature_flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c21c9c622d05"
down_revision = "3ce98448ac72"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_IDCHECK_FRAUD_CONTROLS",
        isActive=True,
        description="Active les contrôles de sécurité en sortie du process ID Check",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
