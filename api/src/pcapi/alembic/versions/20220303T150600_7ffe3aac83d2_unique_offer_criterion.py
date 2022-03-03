"""unique_offer_criterion
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7ffe3aac83d2"
down_revision = "75adc304cc89"
branch_labels = None
depends_on = None


def upgrade():
    # Delete duplicates before creating unique constraint
    op.execute(
        """
        DELETE
        FROM offer_criterion
        WHERE id IN (
            SELECT DISTINCT
                oc1.id
            FROM
                offer_criterion oc1, offer_criterion oc2
            WHERE
                oc1.id > oc2.id
                AND oc1."offerId" = oc2."offerId"
                AND oc1."criterionId" = oc2."criterionId"
        );
        """
    )
    op.create_unique_constraint("unique_offer_criterion", "offer_criterion", ["offerId", "criterionId"])


def downgrade():
    op.drop_constraint("unique_offer_criterion", "offer_criterion", type_="unique")
