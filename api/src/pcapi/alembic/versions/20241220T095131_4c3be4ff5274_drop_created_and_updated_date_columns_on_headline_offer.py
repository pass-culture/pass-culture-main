"""
drop dateCreated and dateUpdated columns from headline_offer table
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4c3be4ff5274"
down_revision = "4c53718279e7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('ALTER TABLE headline_offer DROP COLUMN IF EXISTS "dateUpdated"')
    op.execute('ALTER TABLE headline_offer DROP COLUMN IF EXISTS "dateCreated"')


def downgrade() -> None:
    op.execute(
        'ALTER TABLE headline_offer ADD COLUMN IF NOT EXISTS "dateCreated" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()'
    )
    op.execute(
        'ALTER TABLE headline_offer ADD COLUMN IF NOT EXISTS "dateUpdated" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()'
    )
