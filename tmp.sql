SELECT *
FROM (SELECT (SELECT coalesce(sum(criterion."scoreDelta"), 0) AS coalesce_1
      FROM criterion, offer_criterion
      WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) AS anon_2,
  offer."idAtProviders" AS "offer_idAtProviders",
  offer."dateModifiedAtLastProvider" AS "offer_dateModifiedAtLastProvider", offer."isActive" AS "offer_isActive",
  offer."extraData" AS "offer_extraData", offer.id AS offer_id, offer."productId" AS "offer_productId",
  offer."venueId" AS "offer_venueId", offer."bookingEmail" AS "offer_bookingEmail", offer.type AS offer_type,
  offer.name AS offer_name, offer.description AS offer_description, offer.conditions AS offer_conditions,
  offer."ageMin" AS "offer_ageMin", offer."ageMax" AS "offer_ageMax", offer.url AS offer_url,
  offer."mediaUrls" AS "offer_mediaUrls", offer."durationMinutes" AS "offer_durationMinutes",
  offer."isNational" AS "offer_isNational", offer."isDuo" AS "offer_isDuo", offer."dateCreated" AS "offer_dateCreated",
  offer."lastProviderId" AS "offer_lastProviderId", row_number()
                                                    OVER (
                                                      PARTITION BY offer.type, offer.url IS NULL ) AS anon_3
FROM offer
WHERE offer.id IN ( SELECT DISTINCT ON (offer.id) offer.id
FROM offer JOIN venue ON offer."venueId" = venue.id JOIN offerer ON offerer.id = venue."managingOffererId"
WHERE offer."isActive" = TRUE AND venue."validationToken" IS NULL AND ( EXISTS ( SELECT 1
FROM mediation
WHERE mediation."offerId" = offer.id AND mediation."isActive"))
      AND (venue."departementCode" IN ('75', '77', '78', '91', '92', '93', '94', '95')
           OR offer."isNational" = TRUE ) AND (EXISTS(SELECT 1
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
      AND offerer."isActive" = TRUE AND offerer."validationToken" IS NULL AND offer.type != 'ThingType.ACTIVATION'
      AND offer.type != 'EventType.ACTIVATION' AND offer.id NOT IN ( SELECT stock."offerId"
FROM booking JOIN stock ON stock.id = booking."stockId"
WHERE booking."userId" = 152) AND offer.id NOT IN ( SELECT "offerId"
FROM favorite
WHERE favorite."userId" = 152)) ORDER BY row_number() OVER ( PARTITION BY offer.type, offer.url IS NULL )
LIMIT 30 OFFSET 0) AS anon_1
LEFT OUTER JOIN product AS product_1 ON product_1.id = anon_1."offer_productId"
LEFT OUTER JOIN mediation AS mediation_1 ON anon_1.offer_id = mediation_1."offerId" ORDER BY anon_1.anon_3;

'beginningDatetime_1':datetime.datetime(2020, 1, 10, 14, 45, 28, 937187), 'bookingLimitDatetime_1':datetime.datetime(2020, 1, 10, 14, 45, 28, 937245), 'coalesce_3':0, 'greatest_2':0, 'param_1':0, 'type_1':'EventType.ACTIVATION', 'type_2':'ThingType.ACTIVATION', 'userId_1':152, 'userId_2':152, 'param_2':30, 'param_3':0}
{'coalesce_2':0, 'departementCode_1':'75', 'departementCode_2':'77', 'departementCode_3':'78', 'departementCode_4':'91', 'departementCode_5':'92', 'departementCode_6':'93', 'departementCode_7':'94', 'departementCode_8':'95', 'beginningDatetime_1':datetime.datetime(2020, 1, 10, 14, 45, 28, 937187), 'bookingLimitDatetime_1':datetime.datetime(2020, 1, 10, 14, 45, 28, 937245), 'coalesce_3':0, 'greatest_2':0, 'param_1':0, 'type_1':'EventType.ACTIVATION', 'type_2':'ThingType.ACTIVATION', 'userId_1':152, 'userId_2':152, 'param_2':30, 'param_3':0}










===========================================================================================================
===========================================================================================================
===========================================================================================================
===========================================================================================================
===========================================================================================================


SELECT
  anon_1.anon_2                             AS anon_1_anon_2,
  anon_1."offer_idAtProviders"              AS "anon_1_offer_idAtProviders",
  anon_1."offer_dateModifiedAtLastProvider" AS "anon_1_offer_dateModifiedAtLastProvider",
  anon_1."offer_isActive"                   AS "anon_1_offer_isActive",
  anon_1."offer_extraData"                  AS "anon_1_offer_extraData",
  anon_1.offer_id                           AS anon_1_offer_id,
  anon_1."offer_productId"                  AS "anon_1_offer_productId",
  anon_1."offer_venueId"                    AS "anon_1_offer_venueId",
  anon_1."offer_bookingEmail"               AS "anon_1_offer_bookingEmail",
  anon_1.offer_type                         AS anon_1_offer_type,
  anon_1.offer_name                         AS anon_1_offer_name,
  anon_1.offer_description                  AS anon_1_offer_description,
  anon_1.offer_conditions                   AS anon_1_offer_conditions,
  anon_1."offer_ageMin"                     AS "anon_1_offer_ageMin",
  anon_1."offer_ageMax"                     AS "anon_1_offer_ageMax",
  anon_1.offer_url                          AS anon_1_offer_url,
  anon_1."offer_mediaUrls"                  AS "anon_1_offer_mediaUrls",
  anon_1."offer_durationMinutes"            AS "anon_1_offer_durationMinutes",
  anon_1."offer_isNational"                 AS "anon_1_offer_isNational",
  anon_1."offer_isDuo"                      AS "anon_1_offer_isDuo",
  anon_1."offer_dateCreated"                AS "anon_1_offer_dateCreated",
  anon_1."offer_lastProviderId"             AS "anon_1_offer_lastProviderId",
  anon_1.anon_3                             AS anon_1_anon_3,
  product_1.id                              AS product_1_id,
  product_1."idAtProviders"                 AS "product_1_idAtProviders",
  product_1."dateModifiedAtLastProvider"    AS "product_1_dateModifiedAtLastProvider",
  product_1."extraData"                     AS "product_1_extraData",
  product_1."thumbCount"                    AS "product_1_thumbCount",
  product_1.type                            AS product_1_type,
  product_1.name                            AS product_1_name,
  product_1.description                     AS product_1_description,
  product_1.conditions                      AS product_1_conditions,
  product_1."ageMin"                        AS "product_1_ageMin",
  product_1."ageMax"                        AS "product_1_ageMax",
  product_1."mediaUrls"                     AS "product_1_mediaUrls",
  product_1.url                             AS product_1_url,
  product_1."durationMinutes"               AS "product_1_durationMinutes",
  product_1."isNational"                    AS "product_1_isNational",
  product_1."owningOffererId"               AS "product_1_owningOffererId",
  product_1."lastProviderId"                AS "product_1_lastProviderId",
  mediation_1."idAtProviders"               AS "mediation_1_idAtProviders",
  mediation_1."dateModifiedAtLastProvider"  AS "mediation_1_dateModifiedAtLastProvider",
  mediation_1."isActive"                    AS "mediation_1_isActive",
  mediation_1."thumbCount"                  AS "mediation_1_thumbCount",
  mediation_1.id                            AS mediation_1_id,
  mediation_1."frontText"                   AS "mediation_1_frontText",
  mediation_1."backText"                    AS "mediation_1_backText",
  mediation_1.credit                        AS mediation_1_credit,
  mediation_1."dateCreated"                 AS "mediation_1_dateCreated",
  mediation_1."authorId"                    AS "mediation_1_authorId",
  mediation_1."offerId"                     AS "mediation_1_offerId",
  mediation_1."tutoIndex"                   AS "mediation_1_tutoIndex",
  mediation_1."lastProviderId"              AS "mediation_1_lastProviderId"
FROM (SELECT (SELECT coalesce(sum(criterion."scoreDelta"), % (coalesce_2) s) AS coalesce_1
      FROM criterion, offer_criterion
      WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) AS anon_2,
  offer."idAtProviders" AS "offer_idAtProviders",
  offer."dateModifiedAtLastProvider" AS "offer_dateModifiedAtLastProvider", offer."isActive" AS "offer_isActive",
  offer."extraData" AS "offer_extraData", offer.id AS offer_id, offer."productId" AS "offer_productId",
  offer."venueId" AS "offer_venueId", offer."bookingEmail" AS "offer_bookingEmail", offer.type AS offer_type,
  offer.name AS offer_name, offer.description AS offer_description, offer.conditions AS offer_conditions,
  offer."ageMin" AS "offer_ageMin", offer."ageMax" AS "offer_ageMax", offer.url AS offer_url,
  offer."mediaUrls" AS "offer_mediaUrls", offer."durationMinutes" AS "offer_durationMinutes",
  offer."isNational" AS "offer_isNational", offer."isDuo" AS "offer_isDuo", offer."dateCreated" AS "offer_dateCreated",
  offer."lastProviderId" AS "offer_lastProviderId", row_number()
                                                    OVER (
                                                      PARTITION BY offer.type, offer.url IS NULL
                                                      ORDER BY (EXISTS(SELECT 1
                                                                       FROM stock
                                                                       WHERE stock."offerId" = offer.id AND
                                                                             (stock."beginningDatetime" IS NULL OR
                                                                              stock."beginningDatetime" > %
                                                                              (beginningDatetime_1)S AND stock.
                                                                                                     "beginningDatetime"
                                                                                                     < %(
                                                                                 beginningDatetime_2) S))) DESC, (SELECT
                                                                                                                    coalesce(
                                                                                                                        sum(
                                                                                                                            criterion."scoreDelta"),
                                                                                                                    %
                                                                                                                    (coalesce_2) s) AS coalesce_1
FROM criterion, offer_criterion
WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) DESC, random()) AS anon_3
FROM offer
WHERE offer.id IN ( SELECT DISTINCT ON (offer.id) offer.id
FROM offer JOIN venue ON offer."venueId" = venue.id JOIN offerer ON offerer.id = venue."managingOffererId"
WHERE offer."isActive" = TRUE AND venue."validationToken" IS NULL AND ( EXISTS ( SELECT 1
FROM mediation
WHERE mediation."offerId" = offer.id AND mediation."isActive")) AND (venue."departementCode" IN (%(departementCode_1) S, %(departementCode_2) S, %(departementCode_3) S, %(departementCode_4) S, %(departementCode_5) S, %(departementCode_6) S, %(departementCode_7) S, %(departementCode_8) S ) OR offer."isNational" = TRUE ) AND ( EXISTS ( SELECT 1
FROM stock
WHERE stock."offerId" = offer.id AND stock."isSoftDeleted" = FALSE AND (stock."beginningDatetime" > %(beginningDatetime_3) S OR stock."beginningDatetime" IS NULL ) AND (stock."bookingLimitDatetime" > %(bookingLimitDatetime_1) S OR stock."bookingLimitDatetime" IS NULL ) AND (stock.available IS NULL OR ( SELECT greatest(stock.available - COALESCE (sum(booking.quantity), %(coalesce_3) S ), %(greatest_2) S ) AS greatest_1
FROM booking
WHERE booking."stockId" = stock.id AND (booking."isUsed" = FALSE AND booking."isCancelled" = FALSE OR booking."isUsed" = TRUE AND booking."dateUsed" > stock."dateModified")) > %(param_1) S ))) AND offerer."isActive" = TRUE AND offerer."validationToken" IS NULL AND offer.type != %(type_1) S AND offer.type != %(type_2) S AND offer.id NOT IN ( SELECT stock."offerId"
FROM booking JOIN stock ON stock.id = booking."stockId"
WHERE booking."userId" = %(userId_1) S ) AND offer.id NOT IN ( SELECT "offerId"
FROM favorite
WHERE favorite."userId" = %(userId_2) S )) ORDER BY row_number() OVER ( PARTITION BY offer.type, offer.url IS NULL ORDER BY ( EXISTS ( SELECT 1
FROM stock
WHERE stock."offerId" = offer.id AND (stock."beginningDatetime" IS NULL OR stock."beginningDatetime" > %(beginningDatetime_1) S AND stock."beginningDatetime" < %(beginningDatetime_2) S ))) DESC, ( SELECT COALESCE (sum(criterion."scoreDelta"), %(coalesce_2) S ) AS coalesce_1
FROM criterion, offer_criterion
WHERE criterion.id = offer_criterion."criterionId" AND offer_criterion."offerId" = offer.id) DESC, random())
LIMIT %(param_2) S OFFSET %(param_3) S ) AS anon_1 LEFT OUTER JOIN product AS product_1 ON product_1.id = anon_1."offer_productId" LEFT OUTER JOIN mediation AS mediation_1 ON anon_1.offer_id = mediation_1."offerId" ORDER BY anon_1.anon_3

-- 2020-01-13 10:25:32,168 INFO sqlalchemy.engine.base.Engine {'coalesce_2': 0, 'beginningDatetime_1': datetime.datetime(2020, 1, 13, 10, 25, 32, 137068), 'beginningDatetime_2': datetime.datetime(2020, 1, 23, 10, 25, 32, 137157), 'departementCode_1': '75', 'departementCode_2': '77', 'departementCode_3': '78', 'departementCode_4': '91', 'departementCode_5': '92', 'departementCode_6': '93', 'departementCode_7': '94', 'departementCode_8': '95', 'beginningDatetime_3': datetime.datetime(2020, 1, 13, 10, 25, 32, 128363), 'bookingLimitDatetime_1': datetime.datetime(2020, 1, 13, 10, 25, 32, 128473), 'coalesce_3': 0, 'greatest_2': 0, 'param_1': 0, 'type_1': 'EventType.ACTIVATION', 'type_2': 'ThingType.ACTIVATION', 'userId_1': 46, 'userId_2': 46, 'param_2': 30, 'param_3': 0}
-- 2020-01-13 10:25:32 INFO     {'coalesce_2': 0, 'beginningDatetime_1': datetime.datetime(2020, 1, 13, 10, 25, 32, 137068), 'beginningDatetime_2': datetime.datetime(2020, 1, 23, 10, 25, 32, 137157), 'departementCode_1': '75', 'departementCode_2': '77', 'departementCode_3': '78', 'departementCode_4': '91', 'departementCode_5': '92', 'departementCode_6': '93', 'departementCode_7': '94', 'departementCode_8': '95', 'beginningDatetime_3': datetime.datetime(2020, 1, 13, 10, 25, 32, 128363), 'bookingLimitDatetime_1': datetime.datetime(2020, 1, 13, 10, 25, 32, 128473), 'coalesce_3': 0, 'greatest_2': 0, 'param_1': 0, 'type_1': 'EventType.ACTIVATION', 'type_2': 'ThingType.ACTIVATION', 'userId_1': 46, 'userId_2': 46, 'param_2': 30, 'param_3': 0}