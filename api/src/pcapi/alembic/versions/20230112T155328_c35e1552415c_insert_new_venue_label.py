"""insert_new_venue_label
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c35e1552415c"
down_revision = "2e171418aa71"
branch_labels = None
depends_on = None


def upgrade():
    last_id = op.get_bind().execute("SELECT MAX(id) FROM venue_label").scalar()
    new_id = str(last_id + 1)
    op.execute(
        sa.text("INSERT INTO venue_label (id, label) VALUES (" + new_id + ", 'Centre national de la marionnette')")
    )
    pass


def downgrade():
    op.execute("DELETE FROM venue_label WHERE label = 'Centre national de la marionnette'")
    pass
