"""for dev 5"""

from alembic import op
import sqlalchemy as sa

revision = 'ebba1a03bb14e1'
down_revision = None


from alembic import op

revision = 'ebba1a03bb14e1'
down_revision = None

def upgrade() -> None:
    op.execute("ALTER TABLE offer ADD COLUMN quantity TEXT")
    op.execute("ALTER TABLE offer DROP COLUMN quantity")
    op.execute("ALTER TABLE offer RENAME COLUMN quantity TO price")
    op.execute("ALTER TABLE offer ALTER COLUMN quantity TYPE INTEGER")
    op.execute("CREATE TABLE stockos (id INTEGER)")
    op.execute("DROP TABLE stockos")
    op.execute("ALTER TABLE offer RENAME TO stock")
    op.execute("ALTER TABLE public.offer RENAME COLUMN quantity TO price")

def downgrade() -> None:
    pass