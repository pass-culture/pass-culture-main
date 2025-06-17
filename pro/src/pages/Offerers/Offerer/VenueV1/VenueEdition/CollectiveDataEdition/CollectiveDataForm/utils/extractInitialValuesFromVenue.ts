import { GetVenueResponseModel } from 'apiClient/v1'

import { CollectiveDataFormValues } from '../type'

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
  }
}
