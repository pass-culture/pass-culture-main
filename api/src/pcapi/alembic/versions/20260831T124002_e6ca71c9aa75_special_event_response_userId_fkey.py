"""Add ondelete=SET NULL on special_event_response_userId_fkey (2/3)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e6ca71c9aa75"
down_revision = "d01b0452ca65"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "special_event_response_userId_fkey",
        "special_event_response",
        "user",
        ["userId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("special_event_response_userId_fkey", "special_event_response", type_="foreignkey")
