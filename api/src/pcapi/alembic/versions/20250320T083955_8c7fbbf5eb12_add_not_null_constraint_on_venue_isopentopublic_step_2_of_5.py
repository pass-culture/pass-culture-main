"""Add NOT NULL constraint on "venue.isOpenToPublic" (step 2 of 5)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8c7fbbf5eb12"
down_revision = "9f0aa140fab6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE venue SET "isOpenToPublic"=false WHERE "isOpenToPublic" is NULL;
        """
    )


def downgrade() -> None:
    pass
