"""Drop unique constraint product_mediation_uuid_key."""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "71bd3fc0eca9"
down_revision = "3d56fe5bbe15"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE product_mediation DROP CONSTRAINT IF EXISTS product_mediation_uuid_key;")


def downgrade() -> None:
    pass
