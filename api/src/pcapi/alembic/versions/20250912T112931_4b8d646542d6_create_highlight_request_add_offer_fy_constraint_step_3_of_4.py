"""Set foreign key highlight_request.offerId (1/2)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4b8d646542d6"
down_revision = "343cd453bc6f"
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
    op.drop_constraint("highlight_request_offerId_fkey", "highlight_request", type_="foreignkey")
