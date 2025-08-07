"""
Add index on collective offer template on locationType and offererAddressId
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "48519dd044d4"
down_revision = "99563d5b0706"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_collective_offer_template_locationType_offererAddressId",
            table_name="collective_offer_template",
            columns=["locationType", "offererAddressId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_collective_offer_template_locationType_offererAddressId",
            table_name="collective_offer_template",
            postgresql_concurrently=True,
            if_exists=True,
        )
