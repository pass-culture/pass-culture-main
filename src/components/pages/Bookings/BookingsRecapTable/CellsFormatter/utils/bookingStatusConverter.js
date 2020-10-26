import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../../utils/date'

const BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: 'validated',
    status: 'validé',
    tooltip_status: 'Réservation validée',
    historyClassName: 'bs-history-validated',
    statusClassName: 'booking-status-validated',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-double-validated',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    tooltip_status: 'Réservation annulée',
    historyClassName: 'bs-history-cancelled',
    statusClassName: 'booking-status-cancelled',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: 'ico-status-cancelled',
    svgIconFilename: 'ico-status-cancelled',
  },
  {
    id: 'booked',
    status: 'réservé',
    tooltip_status: 'Réservé',
    historyClassName: 'bs-history-booked',
    statusClassName: 'booking-status-booked',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-booked',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    tooltip_status: 'Remboursée',
    historyClassName: 'bs-history-reimbursed',
    statusClassName: 'booking-status-reimbursed',
    dateFormat: FORMAT_DD_MM_YYYY,
    svgIconFilename: 'ico-status-reimbursed',
  },
  {
    id: 'confirmed',
    status: 'confirmé',
    tooltip_status: 'Réservation confirmée',
    historyClassName: 'bs-history-confirmed',
    statusClassName: 'booking-status-confirmed',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-double-validated',
  },
]

export function getBookingStatusDisplayInformations(bookingStatus) {
  return BOOKING_STATUS_DISPLAY_INFORMATIONS.find(({ id }) => bookingStatus.toLowerCase() === id)
}
