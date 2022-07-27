import { VenueCollectiveInformation } from 'core/Venue/types'

import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from '../initialValues'
import { CollectiveDataFormValues } from '../type'

type CollectiveDataFormValuesWithoutSearchField = Omit<
  CollectiveDataFormValues,
  | 'search-collectiveStudents'
  | 'search-collectiveDomains'
  | 'search-collectiveNetwork'
  | 'search-collectiveInterventionArea'
>

const getValue = <T extends keyof CollectiveDataFormValuesWithoutSearchField>(
  venue: VenueCollectiveInformation,
  key: T
): CollectiveDataFormValues[T] => {
  if (key === 'collectiveDomains') {
    return (venue.collectiveDomains?.map(domain => domain.id.toString()) ??
      COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectiveDomains) as CollectiveDataFormValues[T]
  }

  if (key === 'collectiveLegalStatus') {
    return (venue.collectiveLegalStatus?.id?.toString() ??
      COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectiveLegalStatus) as CollectiveDataFormValues[T]
  }

  return (venue[key] ??
    COLLECTIVE_DATA_FORM_INITIAL_VALUES[key]) as CollectiveDataFormValues[T]
}

export const extractInitialValuesFromVenue = (
  venue: VenueCollectiveInformation
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
  'search-collectiveStudents': '',
  'search-collectiveDomains': '',
  'search-collectiveNetwork': '',
  'search-collectiveInterventionArea': '',
})
