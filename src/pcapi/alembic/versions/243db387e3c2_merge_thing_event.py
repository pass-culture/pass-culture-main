"""Merge tables Thing and Event

Revision ID: 243db387e3c2
Revises: c3fb24563ff0
Create Date: 2019-04-03 12:48:45.518970

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '243db387e3c2'
down_revision = 'c3fb24563ff0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('event', sa.Column('url', sa.VARCHAR(255), nullable=True))
    op.alter_column('event', 'durationMinutes', existing_type=sa.Integer, nullable=True)
    op.drop_column('event', 'accessibility')
    op.add_column('event', sa.Column('thingId', sa.BigInteger, nullable=True))
    op.drop_constraint('check_duration_minutes_not_null_for_event', 'offer')
    op.drop_constraint('check_offer_has_thing_xor_event', 'offer')

    op.execute("""
    INSERT INTO
        event ("idAtProviders", "dateModifiedAtLastProvider", "extraData", "thumbCount", "firstThumbDominantColor",
        "type", "name", "description", "mediaUrls", "url", "isNational", "lastProviderId", "thingId")
    SELECT
        "idAtProviders", "dateModifiedAtLastProvider", "extraData", "thumbCount", "firstThumbDominantColor",
        "type", "name", "description", "mediaUrls", "url", "isNational", "lastProviderId", "id"
    FROM
        thing
    ;
    """)

    op.execute("""
    UPDATE offer
    SET "eventId" = event.id 
    FROM event
    WHERE event."thingId" = offer."thingId";
    """)

    op.drop_column('event', 'thingId')
    op.drop_constraint('offer_thingId_fkey', 'offer', type_='foreignkey')
    op.drop_table('thing')

    op.execute("""
    ALTER TABLE "event" RENAME CONSTRAINT "event_pkey" TO "product_pkey";
    ALTER TABLE "event" RENAME TO "product";
    ALTER SEQUENCE "event_id_seq" RENAME TO "product_id_seq";
    ALTER TABLE "offer" RENAME CONSTRAINT "offer_eventId_fkey" TO "offer_productId_fkey";
    ALTER INDEX "ix_offer_eventId" RENAME TO "ix_offer_productId";
    """)

    op.alter_column('offer', 'eventId', new_column_name='productId', nullable=False)


def downgrade():
    pass
