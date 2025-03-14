"""Update venue isOpenToPublic field to not nullable"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f214ce54efc6"
down_revision = "ddf63ed44a81"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE venue SET isOpenToPublic = 0 WHERE isOpenToPublic is NULL;
        """
    )
    op.alter_column("venue", "isOpenToPublic", nullable=False, default=False)


def downgrade() -> None:
    op.alter_column("venue", "isOpenToPublic", nullable=True)
