"""Add venue to CustomReimbursementRule"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b5ae2a2f7d59"
down_revision = "025c622f64f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("custom_reimbursement_rule", sa.Column("venueId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "custom_reimbursement_rule_venueId_fkey", "custom_reimbursement_rule", "venue", ["venueId"], ["id"]
    )
    op.drop_constraint("offer_or_offerer_check", "custom_reimbursement_rule")
    op.create_check_constraint(
        "offer_or_venue_or_offerer_check",
        "custom_reimbursement_rule",
        'num_nonnulls("offerId", "venueId", "offererId") = 1',
    )
    op.execute(
        """
    CREATE OR REPLACE FUNCTION check_venue_has_siret()
    RETURNS TRIGGER AS $$
    BEGIN
      IF
       NOT NEW."venueId" IS NULL THEN
        IF
         (
          (
           SELECT venue.siret
           FROM venue
            WHERE "id"=NEW."venueId"
          ) IS NULL
         )
        THEN
        RAISE EXCEPTION 'venueHasNoSiret'
        USING HINT = 'the venue must have a siret';
       END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS check_venue_has_siret ON "custom_reimbursement_rule";
    CREATE TRIGGER check_venue_has_siret
    AFTER INSERT OR UPDATE ON custom_reimbursement_rule
    FOR EACH ROW
    EXECUTE PROCEDURE check_venue_has_siret()
    """
    )


def downgrade() -> None:
    op.drop_constraint("offer_or_venue_or_offerer_check", "custom_reimbursement_rule")
    op.create_check_constraint(
        "offer_or_offerer_check",
        "custom_reimbursement_rule",
        'num_nonnulls("offerId", "offererId") = 1',
    )

    op.drop_constraint("custom_reimbursement_rule_venueId_fkey", "custom_reimbursement_rule", type_="foreignkey")
    op.drop_column("custom_reimbursement_rule", "venueId")
    op.execute('drop trigger if exists check_venue_has_siret on "custom_reimbursement_rule"')
    op.execute("drop function if exists check_venue_has_siret")
