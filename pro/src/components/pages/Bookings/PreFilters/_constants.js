import { startOfDay, subDays } from 'date-fns'

import { BOOKING_STATUS } from 'core/Bookings'
import { getToday } from 'utils/date'

export const ALL_VENUES = 'all'
export const ALL_DATES = 'all'
export const EMPTY_FILTER_VALUE = ''
export const DEFAULT_BOOKING_PERIOD = 30
export const DEFAULT_PRE_FILTERS = {
  bookingBeginningDate: startOfDay(subDays(getToday(), DEFAULT_BOOKING_PERIOD)),
  bookingEndingDate: startOfDay(getToday()),
  bookingStatusFilter: BOOKING_STATUS.BOOKED,
  offerEventDate: ALL_DATES,
  offerVenueId: ALL_VENUES,
}
export const ALL_VENUES_OPTION = {
  displayName: 'Tous les lieux',
  id: ALL_VENUES,
}
const BOOOKING_STATUS_OPTIONS = [
  { displayName: 'Période de réservation', id: BOOKING_STATUS.BOOKED },
  { displayName: 'Période de validation', id: BOOKING_STATUS.VALIDATED },
  { displayName: 'Période de remboursement', id: BOOKING_STATUS.REIMBURSED },
]
export const [DEFAULT_BOOKING_FILTER, ...BOOOKING_STATUS_FILTER] =
  BOOOKING_STATUS_OPTIONS
