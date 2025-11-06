import { BOOKING_STATUS } from '@/commons/core/Bookings/constants'
import {
  FORMAT_DD_MM_YYYY,
  FORMAT_DD_MM_YYYY_HH_mm,
} from '@/commons/utils/date'
import { TagVariant } from '@/design-system/Tag/Tag'

export const INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    value: BOOKING_STATUS.CANCELLED,
    title: 'Annulée',
    label: 'Réservation annulée',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.ERROR,
  },
  {
    value: BOOKING_STATUS.CONFIRMED,
    title: 'Confirmée',
    label: 'Réservation confirmée',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.SUCCESS,
  },
  {
    value: BOOKING_STATUS.REIMBURSED,
    title: 'Remboursée',
    label: 'Remboursée',
    dateFormat: FORMAT_DD_MM_YYYY,
    variant: TagVariant.SUCCESS,
  },
  {
    value: BOOKING_STATUS.BOOKED,
    title: 'Réservée',
    label: 'Réservée',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.WARNING,
  },
  {
    value: BOOKING_STATUS.VALIDATED,
    title: 'Validée',
    label: 'Réservation validée',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.SUCCESS,
  },
]

export const getBookingStatusDisplayInformations = (bookingStatus: string) =>
  INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS.find(
    ({ value }) => bookingStatus.toLowerCase() === value
  )
