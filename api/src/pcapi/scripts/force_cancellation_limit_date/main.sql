update booking
set "cancellationLimitDate" = now()
where id in (
    select booking.id
    from booking
    join stock on stock.id = booking."stockId"
    where stock."offerId" = 428470159
    and booking.status = 'CONFIRMED'
    and booking."dateCreated" < '2026-08-16'
);
