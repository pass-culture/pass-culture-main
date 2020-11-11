"""add thing and event information into offer table plus copy information

Revision ID: 5eeaa2f48327
Revises: 989e483edf93
Create Date: 2019-03-15 10:41:55.958475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5eeaa2f48327"
down_revision = "989e483edf93"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("type", sa.String(50), nullable=True))
    op.add_column("offer", sa.Column("name", sa.String(140), nullable=True))
    op.add_column("offer", sa.Column("description", sa.Text, nullable=True))
    op.add_column("offer", sa.Column("conditions", sa.String(120), nullable=True))
    op.add_column("offer", sa.Column("ageMin", sa.Integer, nullable=True))
    op.add_column("offer", sa.Column("ageMax", sa.Integer, nullable=True))
    op.add_column("offer", sa.Column("url", sa.String(255), nullable=True))
    op.add_column("offer", sa.Column("mediaUrls", sa.ARRAY(sa.String(220)), nullable=True))
    op.add_column("offer", sa.Column("durationMinutes", sa.Integer, nullable=True))
    op.add_column("offer", sa.Column("isNational", sa.Boolean, nullable=True))
    op.add_column("offer", sa.Column("extraData", sa.JSON, nullable=True))

    op.alter_column("thing", "mediaUrls", sa.ARRAY(sa.String(220)))

    op.execute(
        """
    UPDATE offer
    SET type = thing.type,
     name = thing.name,
     description = thing.description,
     url = thing.url,
     "mediaUrls" = thing."mediaUrls",
     "isNational" = thing."isNational"
    FROM
     thing
    WHERE
     thing.id = offer."thingId";
     
    UPDATE offer
    SET type = event.type,
     name = event.name,
     description = event.description,
     conditions = event.conditions,
     "ageMin" = event."ageMin",
     "ageMax" = event."ageMax",
     "mediaUrls" = event."mediaUrls",
     "durationMinutes" = event."durationMinutes",
     "isNational" = event."isNational"
    FROM
     event
    WHERE
     event.id = offer."eventId";
    """
    )

    op.create_check_constraint(
        constraint_name="check_duration_minutes_not_null_for_event",
        table_name="offer",
        condition="""("eventId" IS NULL) OR ("durationMinutes" IS NOT NULL)""",
    )

    op.alter_column("offer", "name", nullable=False)
    op.alter_column("offer", "mediaUrls", nullable=False)
    op.alter_column("offer", "isNational", nullable=False)


def downgrade():
    op.drop_column("offer", "type")
    op.drop_column("offer", "name")
    op.drop_column("offer", "description")
    op.drop_column("offer", "conditions")
    op.drop_column("offer", "ageMin")
    op.drop_column("offer", "ageMax")
    op.drop_column("offer", "url")
    op.drop_column("offer", "mediaUrls")
    op.drop_column("offer", "durationMinutes")
    op.drop_column("offer", "isNational")
    op.drop_column("offer", "extraData")
