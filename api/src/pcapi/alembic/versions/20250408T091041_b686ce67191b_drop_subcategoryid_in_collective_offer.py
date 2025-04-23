"""Drop subcategoryId in CollectiveOffer"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b686ce67191b"
down_revision = "d697168fafe0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_offer", "subcategoryId")


def downgrade() -> None:
    op.add_column("collective_offer", sa.Column("subcategoryId", sa.TEXT(), autoincrement=False, nullable=True))
