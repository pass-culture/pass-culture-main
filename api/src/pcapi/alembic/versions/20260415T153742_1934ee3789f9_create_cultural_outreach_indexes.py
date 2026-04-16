"""create indexes on table "cultural_outreach" """

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1934ee3789f9"
down_revision = "0d2b1fe1f0b9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_cultural_outreach_offerId",
            "cultural_outreach",
            ["offerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_cultural_outreach_status"),
            "cultural_outreach",
            ["status"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_cultural_outreach_status"),
            table_name="cultural_outreach",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            "ix_cultural_outreach_offerId",
            table_name="cultural_outreach",
            postgresql_concurrently=True,
            if_exists=True,
        )
