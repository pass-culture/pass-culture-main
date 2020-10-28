import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../../utils/date'

const BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: 'validated',
    status: 'validé',
    label: 'Réservation validée',
    historyClassName: 'bs-history-validated',
    statusClassName: 'booking-status-validated',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-double-validated',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    label: 'Réservation annulée',
    historyClassName: 'bs-history-cancelled',
    statusClassName: 'booking-status-cancelled',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: 'ico-status-cancelled',
    svgIconFilename: 'ico-status-cancelled',
  },
  {
    id: 'booked',
    status: 'réservé',
    label: 'Réservé',
    historyClassName: 'bs-history-booked',
    statusClassName: 'booking-status-booked',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-booked',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    label: 'Remboursée',
    historyClassName: 'bs-history-reimbursed',
    statusClassName: 'booking-status-reimbursed',
    dateFormat: FORMAT_DD_MM_YYYY,
    svgIconFilename: 'ico-status-reimbursed',
  },
  {
    id: 'confirmed',
    status: 'confirmé',
    label: 'Réservation confirmée',
    historyClassName: 'bs-history-confirmed',
    statusClassName: 'booking-status-confirmed',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-double-validated',
  },
]

export function getBookingStatusDisplayInformations(bookingStatus) {
  return BOOKING_STATUS_DISPLAY_INFORMATIONS.find(({ id }) => bookingStatus.toLowerCase() === id)
}
