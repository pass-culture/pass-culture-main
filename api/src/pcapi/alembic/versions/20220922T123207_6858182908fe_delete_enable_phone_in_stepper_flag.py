"""Delete ENABLE_PHONE_VALIDATION_IN_STEPPER feature flag.
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6858182908fe"
down_revision = "898cc1f49e37"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM feature where name = 'ENABLE_PHONE_VALIDATION_IN_STEPPER'")


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES ('ENABLE_PHONE_VALIDATION_IN_STEPPER', 'Déplace la validation du numéro de téléphone dans le flux du parcours d inscription', true)
    """
    )
