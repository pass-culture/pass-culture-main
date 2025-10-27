"""Drop category column of Permission"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c23249637c33"
down_revision = "8416f459f37b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("permission", "category")


def downgrade() -> None:
    op.add_column("permission", sa.Column("category", sa.Text(), autoincrement=False, nullable=True))
