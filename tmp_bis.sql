SELECT anon_1."idAtProviders"              AS "idAtProviders",
       anon_1."dateModifiedAtLastProvider" AS "dateModifiedAtLastProvider",
       anon_1."isActive"                   AS "isActive",
       anon_1."extraData"                  AS "extraData",
       anon_1.id                           AS id,
       anon_1."productId"                  AS "productId",
       anon_1."venueId"                    AS "venueId",
       anon_1."bookingEmail"               AS "bookingEmail",
       anon_1.type                         AS type,
       anon_1.name                         AS name,
       anon_1.description                  AS description,
       anon_1.conditions                   AS conditions,
       anon_1."ageMin"                     AS "ageMin",
       anon_1."ageMax"                     AS "ageMax",
       anon_1.url                          AS url,
       anon_1."mediaUrls"                  AS "mediaUrls",
       anon_1."durationMinutes"            AS "durationMinutes",
       anon_1."isNational"                 AS "isNational",
       anon_1."isDuo"                      AS "isDuo",
       anon_1."dateCreated"                AS "dateCreated",
       anon_1."lastProviderId"             AS "lastProviderId",
       mediation_1."idAtProviders"               AS "mediation_idAtProviders",
       mediation_1."dateModifiedAtLastProvider"  AS "mediation_dateModifiedAtLastProvider",
       mediation_1."isActive"                    AS "mediation_isActive",
       mediation_1."thumbCount"                  AS "mediation_thumbCount",
       mediation_1.id                            AS mediation_id,
       mediation_1."frontText"                   AS "mediation_frontText",
       mediation_1."backText"                    AS "mediation_backText",
       mediation_1.credit                        AS mediation_credit,
       mediation_1."dateCreated"                 AS "mediation_dateCreated",
       mediation_1."authorId"                    AS "mediation_authorId",
       mediation_1."offerId"                     AS "mediation_offerId",
       mediation_1."tutoIndex"                   AS "mediation_tutoIndex",
       mediation_1."lastProviderId"              AS "mediation_lastProviderId"
FROM (SELECT (SELECT coalesce(sum(criterion."scoreDelta"), 0) AS coalesce_1
              FROM criterion, offer_criterion
              WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) AS anon_2,
             offer."idAtProviders" AS "idAtProviders",
             offer."dateModifiedAtLastProvider" AS "dateModifiedAtLastProvider",
             offer."isActive" AS "isActive",
             offer."extraData" AS "extraData",
             offer.id AS id,
             offer."productId" AS "productId",
             offer."venueId" AS "venueId",
             offer."bookingEmail" AS "bookingEmail", offer.type AS type,
             offer.name AS name,
             offer.description AS description,
             offer.conditions AS conditions,
             offer."ageMin" AS "ageMin",
             offer."ageMax" AS "ageMax",
             offer.url AS url,
             offer."mediaUrls" AS "mediaUrls",
             offer."durationMinutes" AS "durationMinutes",
             offer."isNational" AS "isNational",
             offer."isDuo" AS "isDuo",
             offer."dateCreated" AS "dateCreated",
             offer."lastProviderId" AS "lastProviderId",
             row_number()
             OVER (
               PARTITION BY offer.type, offer.url IS NULL
               ORDER BY (EXISTS(SELECT 1
                                FROM stock
                                WHERE stock."offerId" = offer.id AND
                                      (stock."beginningDatetime" IS NULL OR
                                       stock."beginningDatetime" > NOW() AND stock.
                                                                             "beginningDatetime" < NOW() + INTERVAL '10 DAY'))) DESC,
                 (SELECT coalesce(sum(criterion."scoreDelta"), 0) AS coalesce_1
                  FROM criterion, offer_criterion
                  WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) DESC, random()
               ) AS anon_3
      FROM offer
      WHERE offer.id IN ( SELECT DISTINCT ON (offer.id) offer.id
                          FROM offer JOIN venue ON offer."venueId" = venue.id JOIN offerer ON offerer.id = venue."managingOffererId"
                          WHERE offer."isActive" = TRUE AND venue."validationToken" IS NULL AND ( EXISTS ( SELECT 1
                                                                                                           FROM mediation
                                                                                                           WHERE mediation."offerId" = offer.id AND mediation."isActive"))
AND (EXISTS(SELECT 1
                                  FROM stock
                                  WHERE
                                  stock."offerId" = offer.id AND stock."isSoftDeleted" = FALSE AND
(stock."beginningDatetime" > NOW()
OR stock."beginningDatetime" IS NULL)
AND (stock."bookingLimitDatetime" > NOW() OR
                                          stock."bookingLimitDatetime" IS NULL)
AND (stock.available IS NULL OR
(SELECT greatest(stock.available -
                 COALESCE(sum(booking.quantity), 0),
0) AS greatest_1
   FROM booking
   WHERE booking."stockId" = stock.id AND (
booking."isUsed" = FALSE AND
booking."isCancelled" = FALSE
                        OR booking."isUsed" = TRUE AND
                        booking."dateUsed" > stock."dateModified")) > 0)))
AND offerer."isActive" = TRUE
AND offerer."validationToken" IS NULL
          AND offer.type != 'ThingType.ACTIVATION'
          AND offer.type != 'EventType.ACTIVATION') ORDER BY row_number() OVER ( PARTITION BY offer.type, offer.url IS NULL
  ORDER BY ( EXISTS ( SELECT 1
                      FROM stock
                      WHERE stock."offerId" = offer.id AND (stock."beginningDatetime" IS NULL OR stock."beginningDatetime" > NOW()
                                                                                                 AND stock."beginningDatetime" < NOW() + INTERVAL '10 DAY'))) DESC,
    ( SELECT COALESCE (sum(criterion."scoreDelta"), 0) AS coalesce_1
      FROM criterion, offer_criterion
      WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) DESC, random())) AS anon_1
LEFT OUTER JOIN mediation AS mediation_1 ON anon_1.id = mediation_1."offerId"
AND mediation_1."isActive" ORDER BY anon_1.anon_3;