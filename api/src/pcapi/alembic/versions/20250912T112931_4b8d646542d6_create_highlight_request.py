"""Add foreign key to offer on highlight request table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4b8d646542d6"
down_revision = "8d1adabb3690"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "highlight_request_offerId_fkey",
        "highlight_request",
        "offer",
        ["offerId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("highlight_request_offerId_fkey", "highlight_request", type_="foreignkey", if_exists=True)
