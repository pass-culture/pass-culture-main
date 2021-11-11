import { startOfDay, subDays } from 'date-fns'

import { getToday } from 'utils/date'

export const ALL_VENUES = 'all'
export const ALL_DATES = 'all'
export const EMPTY_FILTER_VALUE = ''
export const DEFAULT_BOOKING_PERIOD = 30
export const DEFAULT_PRE_FILTERS = {
  bookingBeginningDate: startOfDay(subDays(getToday(), DEFAULT_BOOKING_PERIOD)),
  bookingEndingDate: startOfDay(getToday()),
  offerEventDate: ALL_DATES,
  offerVenueId: ALL_VENUES,
}
export const ALL_VENUES_OPTION = { displayName: 'Tous les lieux', id: ALL_VENUES }
