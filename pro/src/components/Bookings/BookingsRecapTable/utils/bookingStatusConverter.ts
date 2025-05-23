import { BOOKING_STATUS } from 'commons/core/Bookings/constants'
import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import { TagVariant } from 'design-system/Tag/Tag'

export const INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: BOOKING_STATUS.VALIDATED,
    status: 'Validée',
    label: 'Réservation validée',
    historyClassName: 'bs-history-validated',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.SUCCESS,
  },
  {
    id: BOOKING_STATUS.CANCELLED,
    status: 'Annulée',
    label: 'Réservation annulée',
    historyClassName: 'bs-history-cancelled',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.ERROR,
  },
  {
    id: BOOKING_STATUS.BOOKED,
    status: 'Réservée',
    label: 'Réservée',
    historyClassName: 'bs-history-booked',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.SUCCESS,
  },
  {
    id: BOOKING_STATUS.REIMBURSED,
    status: 'Remboursée',
    label: 'Remboursée',
    historyClassName: 'bs-history-reimbursed',
    dateFormat: FORMAT_DD_MM_YYYY,
    variant: TagVariant.SUCCESS,
  },
  {
    id: BOOKING_STATUS.CONFIRMED,
    status: 'Confirmée',
    label: 'Réservation confirmée',
    historyClassName: 'bs-history-confirmed',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    variant: TagVariant.SUCCESS,
  },
]

export const COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: BOOKING_STATUS.VALIDATED,
    status: 'Terminée',
    variant: TagVariant.SUCCESS,
  },
  {
    id: BOOKING_STATUS.CANCELLED,
    status: 'Annulée',
    variant: TagVariant.ERROR,
  },
  {
    id: BOOKING_STATUS.BOOKED,
    status: 'Réservée',
    variant: TagVariant.SUCCESS,
  },
  {
    id: BOOKING_STATUS.PENDING,
    status: 'Préréservée',
    variant: TagVariant.WARNING,
  },
  {
    id: BOOKING_STATUS.REIMBURSED,
    status: 'Remboursée',
    variant: TagVariant.SUCCESS,
  },
  {
    id: BOOKING_STATUS.CONFIRMED,
    status: 'Confirmée',
    variant: TagVariant.SUCCESS,
  },
]

export const getBookingStatusDisplayInformations = (bookingStatus: string) =>
  INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS.find(
    ({ id }) => bookingStatus.toLowerCase() === id
  )

export const getCollectiveBookingStatusDisplayInformations = (
  bookingStatus: string
) =>
  COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS.find(
    ({ id }) => bookingStatus.toLowerCase() === id
  )
