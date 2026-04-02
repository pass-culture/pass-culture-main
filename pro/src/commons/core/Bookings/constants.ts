import { format, startOfDay, subDays } from 'date-fns'

import { BookingEventType } from '@/apiClient/v1'
import {
  ALL_OFFERER_ADDRESSES,
  ALL_OFFERERS,
} from '@/commons/core/Offers/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { FORMAT_ISO_DATE_ONLY, getToday } from '@/commons/utils/date'

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
  eventType: BookingEventType.BOOKED,
  offerEventDate: ALL_DATES,
  offerVenueId: ALL_VENUES,
  offererAddressId: ALL_OFFERER_ADDRESSES,
  offererId: ALL_OFFERERS,
  offerId: undefined,
}

export const BOOKING_EVENT_TYPE_OPTIONS: SelectOption[] = [
  { label: 'Période de réservation', value: BookingEventType.BOOKED },
  { label: 'Période de validation', value: BookingEventType.VALIDATED },
  { label: 'Période de remboursement', value: BookingEventType.REIMBURSED },
]
