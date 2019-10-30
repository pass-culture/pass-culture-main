import pandas

from models.db import db


def get_offerers_details():
    connection = db.engine.connect()

    offerers_details = pandas.concat(
        [get_creation_dates(connection),
         get_first_stock_creation_dates(connection),
         get_first_booking_creation_dates(connection),
         get_number_of_offers(connection),
         get_number_of_bookings_not_cancelled(connection)],
        axis=1
    )

    return offerers_details


def get_creation_dates(connection):
    query = '''
    SELECT
     id AS offerer_id,
     "dateCreated" AS "Date de création"
    FROM offerer
    '''
    return pandas.read_sql(query, connection, index_col="offerer_id")


def get_first_stock_creation_dates(connection):
    query = '''
    SELECT 
     offerer.id AS offerer_id, 
     MIN(activity.issued_at) AS "Date de création du premier stock"
    FROM offerer 
    LEFT JOIN venue ON venue."managingOffererId" = offerer.id 
    LEFT JOIN offer ON offer."venueId" = venue.id 
    LEFT JOIN stock ON stock."offerId" = offer.id 
    LEFT JOIN activity ON (
     activity.changed_data->>'id'=stock.id::text
     AND activity.table_name='stock' 
     AND verb='insert'
    ) 
    GROUP BY offerer_id
    '''

    return pandas.read_sql(query, connection, index_col='offerer_id')


def get_first_booking_creation_dates(connection):
    query = '''
    SELECT 
     offerer.id AS offerer_id, 
     MIN(booking."dateCreated") AS "Date de première réservation"
    FROM offerer    
    LEFT JOIN venue ON venue."managingOffererId" = offerer.id 
    LEFT JOIN offer ON offer."venueId" = venue.id 
    LEFT JOIN stock ON stock."offerId" = offer.id 
    LEFT JOIN booking ON booking."stockId" = stock.id 
    GROUP BY offerer_id
    '''

    return pandas.read_sql(query, connection, index_col='offerer_id')


def get_number_of_offers(connection):
    query = '''
    SELECT 
     offerer.id AS offerer_id, 
     COUNT(offer.id) AS "Nombre d’offres"
    FROM offerer    
    LEFT JOIN venue ON venue."managingOffererId" = offerer.id 
    LEFT JOIN offer ON offer."venueId" = venue.id 
    GROUP BY offerer_id
    '''

    return pandas.read_sql(query, connection, index_col='offerer_id')


def get_number_of_bookings_not_cancelled(connection):
    query = '''
    SELECT 
     offerer.id AS offerer_id, 
     COUNT(booking.id) AS "Nombre de réservations non annulées"
    FROM offerer 
    LEFT JOIN venue ON venue."managingOffererId" = offerer.id 
    LEFT JOIN offer ON offer."venueId" = venue.id 
    LEFT JOIN stock ON stock."offerId" = offer.id 
    LEFT JOIN booking ON booking."stockId" = stock.id AND booking."isCancelled" IS FALSE
    GROUP BY offerer_id
    '''

    return pandas.read_sql(query, connection, index_col='offerer_id')
