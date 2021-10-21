"""use_roles_instead_of_isbeneficiary_colums
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "5641f4266d73"
down_revision = "e1aaf0bb1ebb"
branch_labels = None
depends_on = None


def upgrade():
    # Create new constraint check_admin_is_never_beneficiary
    op.execute(
        """
        ALTER TABLE "user" ADD CONSTRAINT check_admin_is_never_beneficiary CHECK (
            NOT (('BENEFICIARY'=ANY("roles") OR 'UNDERAGE_BENEFICIARY'=ANY("roles"))
            AND 'ADMIN'=ANY("roles"))
        ) NOT VALID;
        """
    )
    # Validate new constraint check_admin_is_never_beneficiary
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
        """
    )
    op.execute("""ALTER TABLE "user" VALIDATE CONSTRAINT check_admin_is_never_beneficiary;""")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )
    # Remove old constraint check_admin_is_not_beneficiary
    op.drop_constraint("check_admin_is_not_beneficiary", "user")


def downgrade():
    # Recreate old constraint check_admin_is_not_beneficiary
    op.execute(
        """
        ALTER TABLE "user" ADD CONSTRAINT check_admin_is_not_beneficiary CHECK (
            (("isBeneficiary" IS FALSE) OR ("isAdmin" IS FALSE))
        ) NOT VALID;
        """
    )
    # Validate old constraint check_admin_is_not_beneficiary
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
        """
    )
    op.execute("""ALTER TABLE "user" VALIDATE CONSTRAINT check_admin_is_not_beneficiary;""")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )
    # Remove new constraint check_admin_is_never_beneficiary
    op.drop_constraint("check_admin_is_never_beneficiary", "user")
