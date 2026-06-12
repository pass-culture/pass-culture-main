update venue
set
    activity = 'SCIENTIFIC_CULTURE'
where
    activity = 'SCIENCE_CENTRE'
    or (
        "venueTypeCode" = 'SCIENTIFIC_CULTURE'
        and (
            activity is null
            or activity = 'NOT_ASSIGNED'
            or activity = 'OTHER'
            or activity = 'CULTURAL_MEDIATION'
        )
    );