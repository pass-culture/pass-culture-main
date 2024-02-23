select
    jsonb_pretty(json_agg(boost_venues) :: jsonb)
from
    (
        select
            venue.name,
            venue.address,
            venue.latitude,
            venue.longitude,
            venue."departementCode",
            venue."postalCode",
            venue.city,
            boost_cinema_details."cinemaUrl"
        from
            venue
            inner join cinema_provider_pivot ON cinema_provider_pivot."venueId" = venue.id
            inner join boost_cinema_details ON boost_cinema_details."cinemaProviderPivotId" = cinema_provider_pivot.id
        where
            venue.city = 'Paris'
            and venue."isPermanent"
    ) boost_venues;