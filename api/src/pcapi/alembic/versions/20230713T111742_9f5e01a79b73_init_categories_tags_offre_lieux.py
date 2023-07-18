"""init default categories on offer/venue tags
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9f5e01a79b73"
down_revision = "96e489262a9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("INSERT INTO criterion_category (label) VALUES ('Comptage partenaire label et appellation du MC')")
    op.execute("INSERT INTO criterion_category (label) VALUES ('Comptage partenaire EPN')")
    op.execute("INSERT INTO criterion_category (label) VALUES ('Playlist lieux et offres')")
    op.execute(
        'INSERT INTO criterion_category_mapping ("criterionId", "categoryId") '
        "SELECT c.id, ct.id "
        "FROM criterion c, (SELECT id FROM criterion_category WHERE label = "
        "'Playlist lieux et offres') ct"
    )


def downgrade() -> None:
    op.execute(
        'DELETE FROM criterion_category_mapping where "categoryId" = (SELECT id FROM criterion_category '
        "WHERE label = 'playlist-lieux-offres')"
    )
    op.execute("DELETE FROM criterion_category WHERE label = 'Comptage partenaire label et appellation du MC'")
    op.execute("DELETE FROM criterion_category WHERE label = 'Comptage partenaire EPN'")
    op.execute("DELETE FROM criterion_category WHERE label = 'Playlist lieux et offres'")
