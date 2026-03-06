import type { WeekdayOpeningHoursTimespans, WeekdayOpeningHoursTimespansV2 } from '@/apiClient/v1'

import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'
import { getTimetableDefaultOpeningHours } from './getTimetableDefaultOpeningHours'
import { HasDateEnum, type IndividualOfferTimetableFormValues } from './types'

export function getTimetableFormDefaultValues({
  openingHours,
  venueOpeningHours,
  isOhoFFEnabled,
}: {
  openingHours?: WeekdayOpeningHoursTimespans | null
  venueOpeningHours?: WeekdayOpeningHoursTimespansV2 | null
  isOhoFFEnabled: boolean
}) {
  const prefilledOpeningHours = getTimetableDefaultOpeningHours({
    offerOpeningHours: openingHours,
    venueOpeningHours: venueOpeningHours,
  })

  return {
    timetableType:
      !isOhoFFEnabled || areOpeningHoursEmpty(openingHours)
        ? 'calendar'
        : 'openingHours',
    openingHours: prefilledOpeningHours,
    hasStartDate: HasDateEnum.NO, //  TODO : retrieve the openingHours startDate when it exists on the model
    hasEndDate: HasDateEnum.NO, //  TODO : retrieve the openingHours endDate when it exists on the model
    startDate: null, //  TODO : retrieve the openingHours startDate when it exists on the model
    endDate: null, //  TODO : retrieve the openingHours endDate when it exists on the model
  } satisfies IndividualOfferTimetableFormValues
}
