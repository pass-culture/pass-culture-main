-- gh workflow run on_dispatch_pcapi_console_job.yaml \
--   -f ENVIRONMENT_SHORT_NAME=tst \
--   -f RESOURCES="512Mi/.5" \
--   -f BRANCH_NAME=PC-42764-mettre-les-labels-a-null-pour-les-offres-localisees-a-la-venue \
--   -f NAMESPACE=loc_label_null_for_offer_in_venue \
--   -f SCRIPT_ARGUMENTS="";

UPDATE 
    offerer_address
SET label = NULL
WHERE id IN (
    SELECT oa.id
    FROM offerer_address as oa
    JOIN venue ON venue.id = oa."venueId"
    JOIN offerer_address as venue_oa ON venue_oa."venueId" = venue.id AND venue_oa.type = 'VENUE_LOCATION'
    WHERE
        oa.type = 'OFFER_LOCATION'
    AND venue_oa."addressId" = oa."addressId"
    AND oa.label = venue."publicName"
)
