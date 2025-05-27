"""Remove on delete cascade rule on `offerer_provider.offererId`"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0ac13179460c"
down_revision = "0c2a733b47a6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("offerer_provider_offererId_fkey", "offerer_provider", type_="foreignkey")
    op.create_foreign_key(
        "offerer_provider_offererId_fkey",
        "offerer_provider",
        "offerer",
        ["offererId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("offerer_provider_offererId_fkey", "offerer_provider", type_="foreignkey")
    op.create_foreign_key(
        "offerer_provider_offererId_fkey",
        "offerer_provider",
        "offerer",
        ["offererId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
