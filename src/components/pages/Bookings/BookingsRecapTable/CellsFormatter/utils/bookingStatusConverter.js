import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../../utils/date'

const BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: 'validated',
    status: 'validé',
    historyClassName: 'bs-history-validated',
    statusClassName: 'booking-status-validated',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-validated',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    historyClassName: 'bs-history-cancelled',
    statusClassName: 'booking-status-cancelled',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    icon: 'ico-status-cancelled',
    svgIconFilename: 'ico-status-cancelled',
  },
  {
    id: 'booked',
    status: 'réservé',
    historyClassName: 'bs-history-booked',
    statusClassName: 'booking-status-booked',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-booked',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    historyClassName: 'bs-history-reimbursed',
    statusClassName: 'booking-status-reimbursed',
    dateFormat: FORMAT_DD_MM_YYYY,
    svgIconFilename: 'ico-status-reimbursed',
  },
  {
    id: 'confirmed',
    status: 'confirmé',
    historyClassName: 'bs-history-confirmed',
    statusClassName: 'booking-status-confirmed',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-validated', // todo missing svg
  },
]

export function getBookingStatusDisplayInformations(bookingStatus) {
  return BOOKING_STATUS_DISPLAY_INFORMATIONS.find(({ id }) => bookingStatus.toLowerCase() === id)
}
