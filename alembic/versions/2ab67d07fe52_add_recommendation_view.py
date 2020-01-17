"""add_recommendation_view

Revision ID: 2ab67d07fe52
Revises: 6b76c225cc26
Create Date: 2020-01-17 14:29:25.391443

"""
from alembic import op

# revision identifiers, used by Alembic.
from models import RecoView

revision = '2ab67d07fe52'
down_revision = '6b76c225cc26'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {RecoView.__tablename__}
                AS SELECT
                   row_number() OVER () AS row_number,
                   anon_1.id                           AS id,
                   anon_1."venueId"                    AS "venueId",
                   anon_1.type                         AS type,
                   anon_1.name                         AS name,
                   anon_1.url                          AS url,
                   anon_1."isNational"                 AS "isNational",
                   mediation_1.id                      AS "mediationId"
                FROM (SELECT 
                         (SELECT coalesce(sum(criterion."scoreDelta"), 0) AS coalesce_1
                            FROM criterion, offer_criterion
                           WHERE criterion.id = offer_criterion."criterionId" 
                             AND offer_criterion."offerId" = offer.id) AS anon_2,
                         offer."isActive" AS "isActive",
                         offer.id AS id,
                         offer."venueId" AS "venueId",
                         offer.type AS type,
                         offer.name AS name,
                         offer.url AS url,
                         offer."isNational" AS "isNational",
                         row_number()
                         OVER (
                           PARTITION BY offer.type, offer.url IS NULL
                           ORDER BY (EXISTS(SELECT 1
                                            FROM stock
                                            WHERE stock."offerId" = offer.id
                                              AND (stock."beginningDatetime" IS NULL
                                                    OR stock."beginningDatetime" > NOW()
                                                   AND stock."beginningDatetime" < NOW() + INTERVAL '10 DAY')
                                     )) DESC,
                                     (SELECT coalesce(sum(criterion."scoreDelta"), 0) AS coalesce_1
                                        FROM criterion, offer_criterion
                                       WHERE criterion.id = offer_criterion."criterionId"
                                         AND offer_criterion."offerId" = offer.id
                                     ) DESC,
                                     random()
                           ) AS anon_3
                      FROM offer
                      WHERE offer.id IN (SELECT DISTINCT ON (offer.id) offer.id
                                          FROM offer
                                          JOIN venue ON offer."venueId" = venue.id
                                          JOIN offerer ON offerer.id = venue."managingOffererId"
                                          WHERE offer."isActive" = TRUE
                                            AND venue."validationToken" IS NULL
                                            AND (EXISTS (SELECT 1
                                                           FROM mediation
                                                          WHERE mediation."offerId" = offer.id
                                                            AND mediation."isActive"))
                                            AND (EXISTS(SELECT 1
                                                          FROM stock
                                                         WHERE stock."offerId" = offer.id
                                                           AND stock."isSoftDeleted" = FALSE
                                                           AND (stock."beginningDatetime" > NOW()
                                                                OR stock."beginningDatetime" IS NULL)
                                                           AND (stock."bookingLimitDatetime" > NOW() 
                                                                OR stock."bookingLimitDatetime" IS NULL)
                                                           AND (stock.available IS NULL
                                                                OR (SELECT greatest(stock.available - COALESCE(sum(booking.quantity), 0),0) AS greatest_1
                                                                      FROM booking
                                                                     WHERE booking."stockId" = stock.id
                                                                       AND (booking."isUsed" = FALSE
                                                                             AND booking."isCancelled" = FALSE
                                                                              OR booking."isUsed" = TRUE
                                                                             AND booking."dateUsed" > stock."dateModified")
                                                                    ) > 0
                                                                )
                                                ))
                                            AND offerer."isActive" = TRUE
                                            AND offerer."validationToken" IS NULL
                                            AND offer.type != 'ThingType.ACTIVATION'
                                            AND offer.type != 'EventType.ACTIVATION'
                                        )
                                        ORDER BY row_number() OVER ( PARTITION BY offer.type,
                                                                                  offer.url IS NULL
                                                                         ORDER BY (EXISTS ( SELECT 1
                                                                                  FROM stock
                                                                                 WHERE stock."offerId" = offer.id 
                                                                                   AND (stock."beginningDatetime" IS NULL
                                                                                        OR stock."beginningDatetime" > NOW()
                                                                                        AND stock."beginningDatetime" < NOW() + INTERVAL '10 DAY')
                                                                         )) DESC,
                                                                         ( SELECT COALESCE (sum(criterion."scoreDelta"), 0) AS coalesce_1
                                                                             FROM criterion, offer_criterion
                                                                            WHERE criterion.id = offer_criterion."criterionId"
                                                                              AND offer_criterion."offerId" = offer.id) DESC,
                                                                             random()
                                                                    )
                      ) AS anon_1
                LEFT OUTER JOIN mediation AS mediation_1 ON anon_1.id = mediation_1."offerId"
                            AND mediation_1."isActive"
                ORDER BY anon_1.anon_3;
    """)


def downgrade():
    op.execute(f"""DROP MATERIALIZED VIEW {RecoView.__tablename__};""")
