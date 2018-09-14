SELECT
        booking_with_venue_information.department_code,
        date_trunc('{{ time_intervall }}', activity.issued_at) AS intervall,
        COUNT booking_with_venue_information.booking_id) AS bookings,
        COUNT(DISTINCT booking_with_venue_information.user_id) AS unique_bookings
FROM
    (SELECT
        booking.id AS booking_id,
        COALESCE(thing_venue."departementCode", event_venue."departementCode") AS department_code,
        booking."userId" AS user_id,
        booking."isCancelled" AS cancelled_booking
    FROM booking
        LEFT JOIN stock ON booking."stockId" = stock.id
        LEFT OUTER JOIN event_occurrence ON stock."eventOccurrenceId" = event_occurrence.id
        LEFT OUTER JOIN offer AS event_offer ON event_occurrence."offerId"=event_offer.id
        LEFT OUTER JOIN offer AS thing_offer ON stock."offerId"=thing_offer.id
        LEFT OUTER JOIN venue AS thing_venue ON thing_offer."venueId"=thing_venue.id
        LEFT OUTER JOIN venue AS event_venue ON event_offer."venueId"=event_venue.id
    ) AS booking_with_venue_information
LEFT JOIN activity ON booking_id = CAST(activity.changed_data->>'id' AS INT)
LEFT JOIN "user" ON "user".id = user_id
WHERE
    "user"."canBookFreeOffers"
    AND NOT cancelled_booking
    AND activity.verb = 'insert'
    AND activity.table_name = 'booking'
GROUP BY date_trunc('{{ time_intervall }}', activity.issued_at), department_code
ORDER BY date_trunc('{{ time_intervall }}', activity.issued_at), department_code