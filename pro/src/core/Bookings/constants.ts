import { format, startOfDay, subDays } from 'date-fns'

import { BookingStatusFilter } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'

export const BOOKING_STATUS = {
  BOOKED: 'booked',
  CANCELLED: 'cancelled',
  CONFIRMED: 'confirmed',
  REIMBURSED: 'reimbursed',
  VALIDATED: 'validated',
  PENDING: 'pending',
}

const ALL_VENUES = 'all'

const ALL_DATES = 'all'

export const EMPTY_FILTER_VALUE = ''

const DEFAULT_BOOKING_PERIOD = 30

export const DEFAULT_PRE_FILTERS = {
  bookingBeginningDate: format(
    startOfDay(subDays(getToday(), DEFAULT_BOOKING_PERIOD)),
    FORMAT_ISO_DATE_ONLY
  ),
  bookingEndingDate: format(startOfDay(getToday()), FORMAT_ISO_DATE_ONLY),
  bookingStatusFilter: BookingStatusFilter.BOOKED,
  offerEventDate: ALL_DATES,
  offerVenueId: ALL_VENUES,
  offerId: undefined,
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
