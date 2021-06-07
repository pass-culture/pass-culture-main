import { subDays } from 'date-fns'

import { getToday } from 'utils/date'

export const ALL_VENUES = 'all'
export const ALL_DATES = 'all'
export const EMPTY_FILTER_VALUE = ''
const DEFAULT_BOOKING_PERIOD = 30
export const DEFAULT_PRE_FILTERS = {
  bookingBeginningDate: subDays(getToday(), DEFAULT_BOOKING_PERIOD),
  bookingEndingDate: getToday(),
  offerEventDate: ALL_DATES,
  offerVenueId: ALL_VENUES,
}
