import pandas

from models.db import db


def get_all_experimentation_users_details():
    connection = db.engine.connect()

    return pandas.concat([get_experimentation_session_column_test(connection)], axis=1)


def get_experimentation_session_column_test(connection):
    query = '''
    SELECT 
     CASE 
      WHEN booking."isUsed" THEN 1
      ELSE 2 
     END AS "Vague d'expérimentation"
    FROM "user"
    LEFT JOIN booking ON booking."userId" = "user".id
    LEFT JOIN stock ON stock.id = booking."stockId"
    LEFT JOIN offer 
     ON offer.id = stock."offerId" 
     AND offer.type = 'ThingType.ACTIVATION'
    WHERE "user"."canBookFreeOffers"
    '''
    return pandas.read_sql_query(query, connection)