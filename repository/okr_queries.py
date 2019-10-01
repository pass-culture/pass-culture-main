import pandas

from models.db import db

recommendation_dates_query = '''
    WITH recommendation_dates AS (
     SELECT
      MIN(recommendation."dateCreated") AS first_recommendation_date,
      MAX(recommendation."dateCreated") AS last_recommendation_date,
      "user".id AS user_id,
      "user"."canBookFreeOffers"
     FROM "user"
     LEFT JOIN recommendation ON recommendation."userId" = "user".id
     GROUP BY "user".id
    )
    '''


def get_beneficiary_users_details():
    connection = db.engine.connect()

    user_details = [
        get_experimentation_sessions(connection),
        get_departments(connection),
        get_activation_dates(connection),
        get_typeform_filling_dates(connection),
        get_first_connection_dates(connection),
        get_date_of_first_bookings(connection),
        get_date_of_second_bookings(connection),
        get_date_of_bookings_on_third_product_type(connection),
        get_last_recommendation_dates(connection),
        get_number_of_bookings(connection),
        get_number_of_non_cancelled_bookings(connection)
    ]
    beneficiary_users_details = pandas.concat(
        user_details,
        axis=1
    )
    return beneficiary_users_details.reset_index(drop=True)


def get_experimentation_sessions(connection):
    query = '''
    WITH experimentation_session AS (
        SELECT
         "isUsed" AS is_used,
         "userId" AS user_id
        FROM booking
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer
         ON offer.id = stock."offerId"
         AND offer.type = 'ThingType.ACTIVATION'
    )

    SELECT
     CASE
      WHEN experimentation_session.is_used THEN 1
      ELSE 2
     END AS "Vague d'expérimentation",
     "user".id AS user_id
    FROM "user"
    LEFT JOIN experimentation_session ON experimentation_session.user_id = "user".id
    WHERE "user"."canBookFreeOffers"

    '''
    return pandas.read_sql_query(query, connection, index_col="user_id")


def get_departments(connection):
    query = '''
    SELECT
     "user"."departementCode" AS "Département",
     "user".id AS user_id
    FROM "user"
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col="user_id")


def get_activation_dates(connection):
    query = '''
    WITH validated_activation_booking AS (
     SELECT activity.issued_at, booking."userId", booking."isUsed" AS is_used
     FROM activity
     JOIN booking
      ON (activity.old_data ->> 'id')::int = booking.id
      AND booking."isUsed"
     JOIN stock
      ON stock.id = booking."stockId"
     JOIN offer
      ON stock."offerId" = offer.id
      AND offer.type = 'ThingType.ACTIVATION'
     WHERE
      activity.table_name='booking'
      AND activity.verb='update'
      AND activity.changed_data ->> 'isUsed'='true'
    )

    SELECT
     CASE
      WHEN validated_activation_booking.is_used THEN validated_activation_booking.issued_at
      ELSE "user"."dateCreated"
     END AS "Date d'activation",
     "user".id as user_id
    FROM "user"
    LEFT JOIN validated_activation_booking
     ON validated_activation_booking."userId" = "user".id
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col='user_id')


def get_typeform_filling_dates(connection):
    query = '''
    WITH typeform_filled AS (
     SELECT activity.issued_at, "user".id AS user_id, "user"."canBookFreeOffers"
     FROM "user"
     LEFT JOIN "activity"
      ON (activity.old_data ->> 'id')::int = "user".id
      AND activity.table_name='user'
      AND activity.verb='update'
      AND activity.changed_data ->> 'needsToFillCulturalSurvey'='false'
      )

    SELECT
     typeform_filled.issued_at AS "Date de remplissage du typeform",
     typeform_filled.user_id AS user_id
    FROM typeform_filled
    WHERE typeform_filled."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col='user_id')


def get_first_connection_dates(connection):
    query = recommendation_dates_query + \
        '''
            SELECT
             recommendation_dates.first_recommendation_date AS "Date de première connexion",
             recommendation_dates.user_id AS user_id
            FROM recommendation_dates
            WHERE recommendation_dates."canBookFreeOffers"
            '''

    return pandas.read_sql(query, connection, index_col='user_id')


def get_date_of_first_bookings(connection):
    query = '''
    WITH bookings_grouped_by_user AS (
    SELECT
     MIN(booking."dateCreated") AS date,
     booking."userId" AS user_id
    FROM booking
    JOIN stock ON stock.id = booking."stockId"
    JOIN offer
     ON offer.id = stock."offerId"
     AND offer.type != 'ThingType.ACTIVATION'
    GROUP BY booking."userId"
    )
    SELECT bookings_grouped_by_user.date AS "Date de première réservation",
    "user".id AS user_id
    FROM "user"
    LEFT JOIN bookings_grouped_by_user ON "user".id = bookings_grouped_by_user.user_id
    WHERE "user"."canBookFreeOffers"
    '''

    return pandas.read_sql(query, connection, index_col='user_id')


def get_date_of_second_bookings(connection):
    query = '''
     WITH second_booking_dates AS (
     SELECT
      ordered_dates."dateCreated" AS date,
      ordered_dates."userId" AS user_id
      FROM (
       SELECT ROW_NUMBER()
       OVER(
        PARTITION BY "userId"
        ORDER BY booking."dateCreated" ASC
        ) AS rank, booking."dateCreated", booking."userId"
       FROM booking
       JOIN stock ON stock.id = booking."stockId"
       JOIN offer ON offer.id = stock."offerId"
       WHERE offer.type != 'ThingType.ACTIVATION'
      ) AS ordered_dates
      WHERE ordered_dates.rank = 2
    )

    SELECT
     second_booking_dates.date AS "Date de deuxième réservation",
     "user".id AS user_id
    FROM "user"
    LEFT JOIN second_booking_dates ON second_booking_dates.user_id = "user".id
    WHERE "user"."canBookFreeOffers"
    '''

    return pandas.read_sql(query, connection, index_col='user_id')


def get_date_of_bookings_on_third_product_type(connection):
    query = '''
    WITH
     bookings_on_distinct_types AS (
      SELECT DISTINCT ON (offer.type, booking."userId") offer.type, booking."userId", booking."dateCreated"
      FROM booking
      JOIN stock ON stock.id = booking."stockId"
      JOIN offer ON offer.id = stock."offerId"
       AND offer.type != 'ThingType.ACTIVATION'
      ORDER BY offer.type, booking."userId", booking."dateCreated" ASC
     ),
     first_booking_on_third_category AS (
      SELECT
       ordered_dates."dateCreated" AS date,
       ordered_dates."userId"
      FROM (
       SELECT
        ROW_NUMBER()
         OVER(
          PARTITION BY "userId"
          ORDER BY bookings_on_distinct_types."dateCreated" ASC
         ) AS rank, bookings_on_distinct_types."dateCreated",
        bookings_on_distinct_types."userId"
       FROM bookings_on_distinct_types
          ) AS ordered_dates
      WHERE ordered_dates.rank = 3
    )

      SELECT
       first_booking_on_third_category.date AS "Date de première réservation dans 3 catégories différentes",
       "user".id as user_id
      FROM "user"
      LEFT JOIN first_booking_on_third_category ON first_booking_on_third_category."userId" = "user".id
      WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col='user_id')


def get_last_recommendation_dates(connection):
    query = recommendation_dates_query + \
        '''
            SELECT
             recommendation_dates.last_recommendation_date AS "Date de dernière recommandation",
             recommendation_dates.user_id AS user_id
            FROM recommendation_dates
            WHERE recommendation_dates."canBookFreeOffers"
            '''
    return pandas.read_sql(query, connection, index_col='user_id')


def get_number_of_bookings(connection):
    query = '''
    WITH bookings_grouped_by_user AS (
     SELECT
      MIN(booking."dateCreated") AS date,
      SUM(booking.quantity) AS number_of_bookings,
      "userId" AS user_id
     FROM booking
     JOIN stock ON stock.id = booking."stockId"
     JOIN offer ON offer.id = stock."offerId"
      AND offer.type != 'ThingType.ACTIVATION'
     GROUP BY user_id
    )

    SELECT
     CASE
      WHEN bookings_grouped_by_user.number_of_bookings IS NULL THEN 0
      ELSE bookings_grouped_by_user.number_of_bookings
     END AS "Nombre de réservations totales",
     "user".id AS user_id
    FROM "user"
    LEFT JOIN bookings_grouped_by_user ON "user".id = bookings_grouped_by_user.user_id
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col='user_id')


def get_number_of_non_cancelled_bookings(connection):
    query = '''
    WITH non_cancelled_bookings_grouped_by_user AS(
    SELECT
     SUM(booking.quantity) AS number_of_bookings,
     "userId" AS user_id
    FROM booking
    JOIN stock ON stock.id = booking."stockId"
    JOIN offer ON offer.id = stock."offerId" AND offer.type != 'ThingType.ACTIVATION'
    WHERE
     booking."isCancelled" IS FALSE
    GROUP BY user_id
    )
    SELECT
     CASE
      WHEN non_cancelled_bookings_grouped_by_user.number_of_bookings IS NULL THEN 0
      ELSE non_cancelled_bookings_grouped_by_user.number_of_bookings
    END AS "Nombre de réservations non annulées",
     "user".id AS user_id
    FROM "user"
    LEFT JOIN non_cancelled_bookings_grouped_by_user ON non_cancelled_bookings_grouped_by_user.user_id = "user".id
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col='user_id')
