"""Add ondelete=SET NULL on special_event_response_userId_fkey (1/3)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d01b0452ca65"
down_revision = "f3917fec135f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("special_event_response_userId_fkey"), "special_event_response", type_="foreignkey")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_foreign_key(
        op.f("special_event_response_userId_fkey"), "special_event_response", "user", ["userId"], ["id"]
    )
