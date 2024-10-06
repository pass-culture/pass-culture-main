"""Delete ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "01840c8231e3"
down_revision = "e1eb1a0b2870"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE",
        isActive=True,
        description="Activer la double écriture dans les tables Address & OffererAddress",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
