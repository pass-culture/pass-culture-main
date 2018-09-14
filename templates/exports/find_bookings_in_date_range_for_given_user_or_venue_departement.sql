SELECT
        booking_id,
        user_id,
        "user"."departementCode",
        activity.id,
        activity.issued_at,
        venue_departement,
        offerer_id,
        offerer_name,
        offer_id,
        event_occurrence_id,
        event_occurrence_beginning_datetime,
        event_id,
        event_name,
        thing_id,
        thing_name
FROM
    (SELECT
        booking.id AS booking_id,
        booking."userId" as user_id,
        COALESCE(thing_venue."departementCode", event_venue."departementCode") AS venue_departement,
        COALESCE(thing_offerer.id, event_offerer.id) AS offerer_id,
        COALESCE(thing_offerer.name, event_offerer.name) AS offerer_name,
        COALESCE(thing_offer.id, event_offer.id) AS offer_id,
        event_occurrence.id AS event_occurrence_id,
        event_occurrence."beginningDatetime" AS event_occurrence_beginning_datetime,
        event.id AS event_id,
        event.name AS event_name,
        thing.id AS thing_id,
        thing.name as thing_name,
        booking."isCancelled" AS cancelled_booking
    FROM booking
        LEFT JOIN stock ON booking."stockId" = stock.id
        LEFT OUTER JOIN event_occurrence ON stock."eventOccurrenceId" = event_occurrence.id
        LEFT OUTER JOIN offer AS event_offer ON event_occurrence."offerId"=event_offer.id
        LEFT OUTER JOIN offer AS thing_offer ON stock."offerId"=thing_offer.id
        LEFT OUTER JOIN venue AS thing_venue ON thing_offer."venueId"=thing_venue.id
        LEFT OUTER JOIN venue AS event_venue ON event_offer."venueId"=event_venue.id
        LEFT OUTER JOIN offerer AS thing_offerer ON thing_venue."managingOffererId"=thing_offerer.id
        LEFT OUTER JOIN offerer AS event_offerer ON event_venue."managingOffererId"=event_offerer.id
        LEFT OUTER JOIN thing ON thing_offer."thingId"=thing.id
        LEFT OUTER JOIN event ON event_offer."eventId"=event.id
    ) AS booking_with_venue_and_offerer_information
LEFT JOIN activity ON booking_id = CAST(activity.changed_data->>'id' AS INT)
LEFT JOIN "user" ON "user".id = user_id
WHERE
    "user"."canBookFreeOffers"
    AND NOT cancelled_booking
    AND activity.verb = 'insert'
    AND activity.table_name = 'booking'
    AND venue_departement= '{{ venue_department }}'
    AND "user"."departementCode" = '{{ user_department }}'
    AND (activity.issued_at BETWEEN '{{ booking_date_min }}' AND '{{ booking_date_max }}')
    AND (
    (event_occurrence_beginning_datetime BETWEEN '{{ event_date_min }}' AND '{{ event_date_max }}')
    OR event_occurrence_beginning_datetime IS NULL
    )
ORDER BY activity.id, booking_id