"""Drop "validationToken" from "user" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "dc623fa7d47b"
down_revision = "9660ff700ed1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("user_validationToken_key", "user", type_="unique")
    op.drop_column("user", "validationToken")


def downgrade() -> None:
    op.execute(
        """
     ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "validationToken" TEXT;
    """
    )
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint("user_validationToken_key", "user", ["validationToken"])
