SELECT
    booking.ean,
    booking.indexed_at,
    booking.bookings,
    substr(booking.name, 0, 50) as short_name,
    booking.object_id as example_id -- count(*) as number_of_lines
FROM
    booking
    join booking b2 on booking.ean = b2.ean
    and booking.bookings <> b2.bookings
GROUP BY
    booking.ean,
    booking.bookings
ORDER BY
    booking.ean ASC,
    booking.indexed_at DESC -- number_of_lines DESC