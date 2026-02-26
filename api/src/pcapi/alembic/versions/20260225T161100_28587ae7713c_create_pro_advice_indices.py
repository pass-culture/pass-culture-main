"""create "offerId" and "venueId" indices on "ProAdvice" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "28587ae7713c"
down_revision = "07d8a1042d5c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_pro_advice_offerId"),
            "pro_advice",
            ["offerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            op.f("ix_pro_advice_offerId"),
            table_name="pro_advice",
            postgresql_concurrently=True,
            if_exists=True,
        )
