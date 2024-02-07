"""reset adage venue address id sequence"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9a4a8ab82816"
down_revision = "ba414c8b1ee4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        -- call setval() because ALTER SEQUENCE does not accept subqueries
        SELECT setval('adage_venue_address_id_seq', (SELECT max(id) + 1000 FROM VENUE), false)
    """
    )


def downgrade() -> None:
    pass
