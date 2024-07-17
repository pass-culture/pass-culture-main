"""
Add foreign key constraint on `venue_provider_permission.venueProviderId`
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "08b944954eba"
down_revision = "e3e9ba056dab"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "venue_provider_permission_venueProviderId_fkey",
        "venue_provider_permission",
        "venue_provider",
        ["venueProviderId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute(
        'ALTER TABLE "venue_provider_permission" VALIDATE CONSTRAINT "venue_provider_permission_venueProviderId_fkey"'
    )


def downgrade() -> None:
    op.drop_constraint(
        "venue_provider_permission_venueProviderId_fkey", "venue_provider_permission", type_="foreignkey"
    )
