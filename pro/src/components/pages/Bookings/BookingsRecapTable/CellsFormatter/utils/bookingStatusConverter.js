import { BOOKING_STATUS } from 'core/Bookings'
import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'

const BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: BOOKING_STATUS.VALIDATED,
    status: 'validé',
    label: 'Réservation validée',
    historyClassName: 'bs-history-validated',
    statusClassName: 'booking-status-validated',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-double-validated',
  },
  {
    id: BOOKING_STATUS.CANCELLED,
    status: 'annulé',
    label: 'Réservation annulée',
    historyClassName: 'bs-history-cancelled',
    statusClassName: 'booking-status-cancelled',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: 'ico-status-cancelled',
    svgIconFilename: 'ico-status-cancelled',
  },
  {
    id: BOOKING_STATUS.BOOKED,
    status: 'réservé',
    label: 'Réservé',
    historyClassName: 'bs-history-booked',
    statusClassName: 'booking-status-booked',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-booked',
  },
  {
    id: BOOKING_STATUS.PENDING,
    status: 'préréservé',
    label: 'Préréservé (scolaire)',
    historyClassName: 'bs-history-pending',
    statusClassName: 'booking-status-pending',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-pending-tag',
  },
  {
    id: BOOKING_STATUS.REIMBURSED,
    status: 'remboursé',
    label: 'Remboursée',
    historyClassName: 'bs-history-reimbursed',
    statusClassName: 'booking-status-reimbursed',
    dateFormat: FORMAT_DD_MM_YYYY,
    svgIconFilename: 'ico-status-reimbursed',
  },
  {
    id: BOOKING_STATUS.CONFIRMED,
    status: 'confirmé',
    label: 'Réservation confirmée',
    historyClassName: 'bs-history-confirmed',
    statusClassName: 'booking-status-confirmed',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-validated',
  },
]

export function getBookingStatusDisplayInformations(bookingStatus) {
  return BOOKING_STATUS_DISPLAY_INFORMATIONS.find(
    ({ id }) => bookingStatus.toLowerCase() === id
  )
}
