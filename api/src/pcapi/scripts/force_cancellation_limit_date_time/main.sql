update booking
set "cancellationLimitDate" = now()
where id in (
    select booking.id
    from booking
    join stock on stock.id = booking."stockId"
    where stock."offerId" = 382881230
    and booking.status = 'CONFIRMED'
    and booking."dateCreated" < '2026-04-20'
);