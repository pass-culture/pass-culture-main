"""in address, fill street field with city if street is null"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f7a60b79eabd"
down_revision = "f9d85badd67d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            UPDATE address SET street = city WHERE street IS NULL;
            """
        )


def downgrade() -> None:
    pass
