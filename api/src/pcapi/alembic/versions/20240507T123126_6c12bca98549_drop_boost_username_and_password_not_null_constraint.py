"""Drop not null constraint for username and password on boost_cinema_details table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6c12bca98549"
down_revision = "7f1b1f973a24"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("boost_cinema_details", "username", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("boost_cinema_details", "password", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    op.alter_column("boost_cinema_details", "password", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("boost_cinema_details", "username", existing_type=sa.TEXT(), nullable=False)
