"""Create new tag: non-diffusible (applied from the code)"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4f6debc0238a"
down_revision = "d787e69663b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO offerer_tag (name, label, description)
        VALUES ('non-diffusible', 'Non-diffusible', 'Structure non-diffusible par l''INSEE')
        ON CONFLICT (name) DO UPDATE SET label='Non-diffusible', description='Structure non-diffusible par l''INSEE'
        """
    )


def downgrade() -> None:
    pass
