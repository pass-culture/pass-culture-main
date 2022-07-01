import { startOfDay, subDays } from 'date-fns'

import { BookingStatusFilter } from 'apiClient/v1'
import { getToday } from 'utils/date'

export const BOOKING_STATUS = {
  BOOKED: 'booked',
  CANCELLED: 'cancelled',
  CONFIRMED: 'confirmed',
  REIMBURSED: 'reimbursed',
  VALIDATED: 'validated',
  PENDING: 'pending',
}

export const ALL_VENUES = 'all'

export const ALL_OFFER_TYPE = 'all'

export const ALL_DATES = 'all'

export const EMPTY_FILTER_VALUE = ''

export const DEFAULT_BOOKING_PERIOD = 30

export const DEFAULT_PRE_FILTERS = {
  bookingBeginningDate: startOfDay(subDays(getToday(), DEFAULT_BOOKING_PERIOD)),
  bookingEndingDate: startOfDay(getToday()),
  bookingStatusFilter: BookingStatusFilter.BOOKED,
  offerEventDate: ALL_DATES,
  offerVenueId: ALL_VENUES,
  offerType: ALL_OFFER_TYPE,
}

export const ALL_VENUES_OPTION = {
  displayName: 'Tous les lieux',
  id: ALL_VENUES,
}

const BOOOKING_STATUS_OPTIONS = [
  { displayName: 'Période de réservation', id: BookingStatusFilter.BOOKED },
  { displayName: 'Période de validation', id: BookingStatusFilter.VALIDATED },
  {
    displayName: 'Période de remboursement',
    id: BookingStatusFilter.REIMBURSED,
  },
]

export const [DEFAULT_BOOKING_FILTER, ...BOOOKING_STATUS_FILTER] =
  BOOOKING_STATUS_OPTIONS
