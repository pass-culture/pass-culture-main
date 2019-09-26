import pandas

from models.db import db


def get_all_beneficiary_users_details():
    connection = db.engine.connect()

    beneficiary_users_details = pandas.concat(
        [
            get_experimentation_session_column(connection),
            get_department_column(connection),
            get_activation_date_column(connection)
        ],
        axis=1
    )
    beneficiary_users_details = beneficiary_users_details.reset_index(drop=True)
    return beneficiary_users_details


def get_experimentation_session_column(connection):
    query = '''
    SELECT 
     CASE 
      WHEN booking."isUsed" THEN 1
      ELSE 2 
     END AS "Vague d'expérimentation",
     "user".id AS user_id
    FROM "user"
    LEFT JOIN booking ON booking."userId" = "user".id
    LEFT JOIN stock ON stock.id = booking."stockId"
    LEFT JOIN offer 
     ON offer.id = stock."offerId" 
     AND offer.type = 'ThingType.ACTIVATION'
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql_query(query, connection, index_col="user_id")


def get_department_column(connection):
    query = '''
    SELECT 
     "user"."departementCode" AS "Département",
     "user".id AS user_id
    FROM "user"    
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col="user_id")


def get_activation_date_column(connection):
    query = '''
    WITH validated_activation_booking AS (
     SELECT activity.issued_at, booking."userId" 
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
      WHEN booking."isUsed" THEN validated_activation_booking.issued_at
      ELSE "user"."dateCreated"
     END AS "Date d'activation",
     "user".id as user_id
    FROM "user"
    LEFT JOIN booking ON booking."userId" = "user".id
    LEFT JOIN stock ON stock.id = booking."stockId"
    LEFT JOIN offer ON offer.id = stock."offerId" 
    LEFT JOIN validated_activation_booking 
     ON validated_activation_booking."userId" = "user".id
     AND offer.type = 'ThingType.ACTIVATION'
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql(query, connection, index_col='user_id')

