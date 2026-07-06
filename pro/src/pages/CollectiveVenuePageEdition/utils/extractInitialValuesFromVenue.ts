import type { GetVenueResponseModel } from '@/apiClient/v1'

import type { CollectiveVenuePageValues } from './type'

export const extractInitialValuesFromVenue = (
  venue: GetVenueResponseModel
): CollectiveVenuePageValues => {
  return {
    collectiveDescription: venue.collectiveDescription ?? '',
    collectiveStudents: venue.collectiveStudents ?? [],
    collectiveWebsite: venue.collectiveWebsite ?? '',
    collectivePhone: venue.collectivePhone ?? '',
    collectiveEmail: venue.collectiveEmail ?? '',
    collectiveLegalStatus: venue.collectiveLegalStatus?.id.toString() ?? '',
    collectiveDomains: venue.collectiveDomains.map((domain) =>
      domain.id.toString()
    ),
    collectiveInterventionArea: venue.collectiveInterventionArea ?? [],
    activity: venue.activity as CollectiveVenuePageValues['activity'], // Force is needed because of "GAMES_CENTRE" which is present in `DisplayableActivity`, but not in `ActivityOpenToPublic | ActivityNotOpenToPublic`
  }
}
