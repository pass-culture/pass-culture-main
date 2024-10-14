import { BOOKING_STATUS } from 'commons/core/Bookings/constants'
import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeDoubleCheckIcon from 'icons/stroke-double-check.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHourglassIcon from 'icons/stroke-hourglass.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'

import styles from './BookingStatus.module.scss'

export const INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: BOOKING_STATUS.VALIDATED,
    status: 'Validée',
    label: 'Réservation validée',
    historyClassName: 'bs-history-validated',
    statusClassName: styles['booking-status-validated'],
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: strokeDoubleCheckIcon,
  },
  {
    id: BOOKING_STATUS.CANCELLED,
    status: 'Annulée',
    label: 'Réservation annulée',
    historyClassName: 'bs-history-cancelled',
    statusClassName: styles['booking-status-cancelled'],
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: strokeWrongIcon,
  },
  {
    id: BOOKING_STATUS.BOOKED,
    status: 'Réservée',
    label: 'Réservée',
    historyClassName: 'bs-history-booked',
    statusClassName: styles['booking-status-booked'],
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: strokeClockIcon,
  },
  {
    id: BOOKING_STATUS.REIMBURSED,
    status: 'Remboursée',
    label: 'Remboursée',
    historyClassName: 'bs-history-reimbursed',
    statusClassName: styles['booking-status-reimbursed'],
    dateFormat: FORMAT_DD_MM_YYYY,
    icon: strokeEuroIcon,
  },
  {
    id: BOOKING_STATUS.CONFIRMED,
    status: 'Confirmée',
    label: 'Réservation confirmée',
    historyClassName: 'bs-history-confirmed',
    statusClassName: styles['booking-status-confirmed'],
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: strokeCheckIcon,
  },
]

export const COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: BOOKING_STATUS.VALIDATED,
    status: 'Terminée',
    statusClassName: styles['booking-status-validated'],
    icon: strokeDoubleCheckIcon,
  },
  {
    id: BOOKING_STATUS.CANCELLED,
    status: 'Annulée',
    statusClassName: styles['booking-status-cancelled'],
    icon: strokeWrongIcon,
  },
  {
    id: BOOKING_STATUS.BOOKED,
    status: 'Réservée',
    statusClassName: styles['booking-status-booked'],
    icon: strokeClockIcon,
  },
  {
    id: BOOKING_STATUS.PENDING,
    status: 'Préréservée',
    statusClassName: styles['booking-status-pending'],
    icon: strokeHourglassIcon,
  },
  {
    id: BOOKING_STATUS.REIMBURSED,
    status: 'Remboursée',
    statusClassName: styles['booking-status-reimbursed'],
    icon: strokeEuroIcon,
  },
  {
    id: BOOKING_STATUS.CONFIRMED,
    status: 'Confirmée',
    statusClassName: styles['booking-status-confirmed'],
    icon: strokeCheckIcon,
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
