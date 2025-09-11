"""delete the offerer tag non-diffusible"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "671f97131193"
down_revision = "f0cb022af752"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM offerer_tag WHERE name = 'non-diffusible'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO offerer_tag (name, label, description)
        VALUES ('non-diffusible', 'Non-diffusible', 'Structure non-diffusible par l''INSEE')
        ON CONFLICT (name) DO UPDATE SET label='Non-diffusible', description='Structure non-diffusible par l''INSEE'
        """
    )


"""Create new tag: non-diffusible"""
