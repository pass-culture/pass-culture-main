"""Add foreign key constraint on event_series_offer_link.offerId"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "042ffc4e412b"
down_revision = "ad37625d13c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "event_series_offer_link_offerId_fkey",
        "event_series_offer_link",
        "offer",
        ["offerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute('ALTER TABLE "event_series_offer_link" VALIDATE CONSTRAINT "event_series_offer_link_offerId_fkey"')


def downgrade() -> None:
    op.drop_constraint(
        "event_series_offer_link_offerId_fkey",
        "event_series_offer_link",
        type_="foreignkey",
    )
