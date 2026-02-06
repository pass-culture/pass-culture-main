import type { GetVenueResponseModel } from '@/apiClient/v1'

import type { CollectiveDataFormValues } from '../type'

export const extractInitialValuesFromVenue = (
  venue: GetVenueResponseModel
): CollectiveDataFormValues => {
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
    activity: venue.activity as CollectiveDataFormValues['activity'], // Force is needed because of "GAMES_CENTRE" which is present in `DisplayableActivity`, but not in `ActivityOpenToPublic | ActivityNotOpenToPublic`
  }
}
