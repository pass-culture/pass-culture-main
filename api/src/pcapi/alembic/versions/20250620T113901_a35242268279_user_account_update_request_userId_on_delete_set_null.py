"""Update foreign key user_account_update_request.userId: on delete set null (1/2)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a35242268279"
down_revision = "902bdb2449b9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("user_account_update_request_userId_fkey"), "user_account_update_request", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("user_account_update_request_userId_fkey"),
        "user_account_update_request",
        "user",
        ["userId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    pass
