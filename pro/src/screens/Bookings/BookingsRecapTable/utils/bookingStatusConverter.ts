import { BOOKING_STATUS } from 'core/Bookings/constants'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeDoubleCheckIcon from 'icons/stroke-double-check.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHourglassIcon from 'icons/stroke-hourglass.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'
import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'

import styles from './BookingStatus.module.scss'

const BOOKING_STATUS_DISPLAY_INFORMATIONS = [
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
    label: 'Réservé',
    historyClassName: 'bs-history-booked',
    statusClassName: styles['booking-status-booked'],
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: strokeClockIcon,
  },
  {
    id: BOOKING_STATUS.PENDING,
    status: 'préréservé',
    label: 'Préréservé (scolaire)',
    historyClassName: 'bs-history-pending',
    statusClassName: styles['booking-status-pending'],
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: strokeHourglassIcon,
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

const COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: BOOKING_STATUS.VALIDATED,
    status: 'Terminée',
    label: 'Votre évènement a eu lieu',
    statusClassName: styles['booking-status-validated'],
    icon: strokeDoubleCheckIcon,
  },
  {
    id: BOOKING_STATUS.CANCELLED,
    status: 'Annulée',
    label: 'Réservation annulée',
    statusClassName: styles['booking-status-cancelled'],
    icon: strokeWrongIcon,
  },
  {
    id: BOOKING_STATUS.BOOKED,
    status: 'Réservée',
    label: 'Le chef d’établissement scolaire a réservé.',
    statusClassName: styles['booking-status-booked'],
    icon: strokeClockIcon,
  },
  {
    id: BOOKING_STATUS.PENDING,
    status: 'Préréservée',
    label: 'L’enseignant a préréservé.',
    statusClassName: styles['booking-status-pending'],
    icon: strokeHourglassIcon,
  },
  {
    id: BOOKING_STATUS.REIMBURSED,
    status: 'Remboursée',
    label: 'La réservation a été remboursée',
    statusClassName: styles['booking-status-reimbursed'],
    icon: strokeEuroIcon,
  },
  {
    id: BOOKING_STATUS.CONFIRMED,
    status: 'Confirmée',
    label: 'L’établissement scolaire ne peut plus annuler la réservation',
    statusClassName: styles['booking-status-confirmed'],
    icon: strokeCheckIcon,
  },
]

export function getBookingStatusDisplayInformations(bookingStatus: string) {
  return BOOKING_STATUS_DISPLAY_INFORMATIONS.find(
    ({ id }) => bookingStatus.toLowerCase() === id
  )
}

export function getCollectiveBookingStatusDisplayInformations(
  bookingStatus: string
) {
  return COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS.find(
    ({ id }) => bookingStatus.toLowerCase() === id
  )
}
