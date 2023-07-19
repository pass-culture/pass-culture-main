import { startOfDay, subDays } from 'date-fns'

import { BookingStatusFilter } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { getToday } from 'utils/date'

export const BOOKING_STATUS = {
  BOOKED: 'booked',
  CANCELLED: 'cancelled',
  CONFIRMED: 'confirmed',
  REIMBURSED: 'reimbursed',
  VALIDATED: 'validated',
  PENDING: 'pending',
}

const ALL_VENUES = 'all'

const ALL_OFFER_TYPE = 'all'

const ALL_DATES = 'all'

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

export const ALL_VENUES_OPTION: SelectOption = {
  label: 'Tous les lieux',
  value: ALL_VENUES,
}

export const BOOKING_STATUS_FILTER_OPTIONS: SelectOption[] = [
  { label: 'Période de réservation', value: BookingStatusFilter.BOOKED },
  { label: 'Période de validation', value: BookingStatusFilter.VALIDATED },
  { label: 'Période de remboursement', value: BookingStatusFilter.REIMBURSED },
]
