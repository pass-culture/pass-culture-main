"""for dev"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = 'c329da08a0ab'
down_revision = '4395343a5323'
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column('achievement', sa.Column('foo', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('achievement', 'foo')
