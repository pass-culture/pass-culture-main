""" Add status column to offerer_invitation table """
from alembic import op
import sqlalchemy as sa

import pcapi.core.offerers.models as offerers_models
import pcapi.utils


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cecf1fb49589"
down_revision = "beb392b1584a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "offerer_invitation",
        sa.Column("status", pcapi.utils.db.MagicEnum(offerers_models.InvitationStatus), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("offerer_invitation", "status")
