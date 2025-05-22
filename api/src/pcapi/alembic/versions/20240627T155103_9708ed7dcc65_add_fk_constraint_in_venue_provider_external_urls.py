"""
Add foreign key constraint on `venue_provider_external_urls.venueProviderId`
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9708ed7dcc65"
down_revision = "4b41a69dfe71"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "venue_provider_external_urls_venueProviderId_fkey",
        "venue_provider_external_urls",
        "venue_provider",
        ["venueProviderId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute(
        'ALTER TABLE "venue_provider_external_urls" VALIDATE CONSTRAINT "venue_provider_external_urls_venueProviderId_fkey"'
    )


def downgrade() -> None:
    op.drop_constraint(
        "venue_provider_external_urls_venueProviderId_fkey", "venue_provider_external_urls", type_="foreignkey"
    )
