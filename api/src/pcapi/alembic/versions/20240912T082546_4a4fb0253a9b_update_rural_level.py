"""Update rural level on EducationalInstitution
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4a4fb0253a9b"
down_revision = "294d3a0492f7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
UPDATE educational_institution
SET "ruralLevel" = CASE
    WHEN "ruralLevel" = 'urbain dense' THEN 'Grands centres urbains'
    WHEN "ruralLevel" = 'urbain densité intermédiaire' THEN 'Centres urbains intermédiaires'
    WHEN "ruralLevel" = 'rural sous forte influence d''un pôle' THEN 'Petites villes'
    WHEN "ruralLevel" = 'rural sous faible influence d''un pôle' THEN 'Bourgs ruraux'
    WHEN "ruralLevel" = 'rural autonome peu dense' THEN 'Rural à habitat dispersé'
    WHEN "ruralLevel" = 'rural autonome très peu dense' THEN 'Rural à habitat très dispersé'
    ELSE "ruralLevel"
END;
               """
    )


def downgrade() -> None:
    op.execute(
        """
UPDATE educational_institution
SET "ruralLevel" = CASE
    WHEN "ruralLevel" = 'Grands centres urbains' THEN 'urbain dense'
    WHEN "ruralLevel" = 'Centres urbains intermédiaires' THEN 'urbain densité intermédiaire'
    WHEN "ruralLevel" = 'Petites villes' THEN 'rural sous forte influence d''un pôle'
    WHEN "ruralLevel" = 'Bourgs ruraux' THEN 'rural sous faible influence d''un pôle'
    WHEN "ruralLevel" = 'Rural à habitat dispersé' THEN 'rural autonome peu dense'
    WHEN "ruralLevel" = 'Rural à habitat très dispersé' THEN 'rural autonome très peu dense'
    ELSE "ruralLevel"
END;
               """
    )
