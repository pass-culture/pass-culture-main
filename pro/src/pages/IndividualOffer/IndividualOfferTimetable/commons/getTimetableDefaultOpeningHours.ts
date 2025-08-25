import type {
  GetVenueResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import { getOpeningHoursFromGetVenueResponseOpeningHours } from '@/pages/VenueEdition/setInitialFormValues'

import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'

export function getTimetableDefaultOpeningHours({
  offerOpeningHours,
  venueOpeningHours,
}: {
  offerOpeningHours?: WeekdayOpeningHoursTimespans | null
  venueOpeningHours?: GetVenueResponseModel['openingHours']
}) {
  const offerOpeningHoursEmpty = areOpeningHoursEmpty(offerOpeningHours)

  //    TODO : do not use the formatting function for venue openingHours when the api model becomes the same
  const formattedVenueOpeningHours =
    getOpeningHoursFromGetVenueResponseOpeningHours(venueOpeningHours)
  const venueOpeningHoursEmpty = areOpeningHoursEmpty(
    formattedVenueOpeningHours
  )

  return offerOpeningHoursEmpty && !venueOpeningHoursEmpty
    ? formattedVenueOpeningHours
    : offerOpeningHours
}
