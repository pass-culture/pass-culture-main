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
    op.execute(sa.text("INSERT INTO venue_label (label) VALUES ('Centre national de la marionnette')"))


def downgrade():
    op.execute("DELETE FROM venue_label WHERE label = 'Centre national de la marionnette'")
