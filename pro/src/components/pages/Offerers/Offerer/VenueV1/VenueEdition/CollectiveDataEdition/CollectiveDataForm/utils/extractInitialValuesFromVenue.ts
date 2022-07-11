import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from '../initialValues'
import { CollectiveDataFormValues } from '../type'
import { GetVenueResponseModel } from 'apiClient/v1'

const getValue = <T extends keyof CollectiveDataFormValues>(
  venue: GetVenueResponseModel,
  key: T
): CollectiveDataFormValues[T] => {
  if (key === 'collectiveDomains') {
    return (venue.collectiveDomains?.map(domain => domain.id.toString()) ??
      COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectiveDomains) as CollectiveDataFormValues[T]
  }

  return (venue[key] ??
    COLLECTIVE_DATA_FORM_INITIAL_VALUES[key]) as CollectiveDataFormValues[T]
}

export const extractInitialValuesFromVenue = (
  venue: GetVenueResponseModel
): CollectiveDataFormValues => ({
  collectiveDescription: getValue(venue, 'collectiveDescription'),
  collectiveStudents: getValue(venue, 'collectiveStudents'),
  collectiveWebsite: getValue(venue, 'collectiveWebsite'),
  collectivePhone: getValue(venue, 'collectivePhone'),
  collectiveEmail: getValue(venue, 'collectiveEmail'),
  collectiveLegalStatus: getValue(venue, 'collectiveLegalStatus'),
  collectiveDomains: getValue(venue, 'collectiveDomains'),
  collectiveNetwork: getValue(venue, 'collectiveNetwork'),
  collectiveInterventionArea: getValue(venue, 'collectiveInterventionArea'),
})
