import type {
  GetVenueResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'

import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'

export function getTimetableDefaultOpeningHours({
  offerOpeningHours,
  venueOpeningHours,
}: {
  offerOpeningHours?: WeekdayOpeningHoursTimespans | null
  venueOpeningHours?: GetVenueResponseModel['openingHours']
}) {
  const offerOpeningHoursEmpty = areOpeningHoursEmpty(offerOpeningHours)

  const venueOpeningHoursEmpty = areOpeningHoursEmpty(venueOpeningHours)

  return offerOpeningHoursEmpty && !venueOpeningHoursEmpty
    ? venueOpeningHours
    : offerOpeningHours
}
