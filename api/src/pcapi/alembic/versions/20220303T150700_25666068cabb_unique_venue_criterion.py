"""unique_venue_criterion
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "25666068cabb"
down_revision = "7ffe3aac83d2"
branch_labels = None
depends_on = None


def upgrade():
    # Delete duplicates before creating unique constraint
    op.execute(
        """
        DELETE
        FROM venue_criterion
        WHERE id IN (
            SELECT DISTINCT
                vc1.id
            FROM
                venue_criterion vc1, venue_criterion vc2
            WHERE
                vc1.id > vc2.id
                AND vc1."venueId" = vc2."venueId"
                AND vc1."criterionId" = vc2."criterionId"
        );
        """
    )
    op.create_unique_constraint("unique_venue_criterion", "venue_criterion", ["venueId", "criterionId"])


def downgrade():
    op.drop_constraint("unique_venue_criterion", "venue_criterion", type_="unique")
