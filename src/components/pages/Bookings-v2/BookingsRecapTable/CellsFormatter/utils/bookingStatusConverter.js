import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../../utils/date'

const BOOKING_STATUS_DISPLAY_INFORMATIONS = [
  {
    id: 'validated',
    status: 'validé',
    className: 'validated',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-validated',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    className: 'cancelled',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-cancelled',
  },
  {
    id: 'booked',
    status: 'réservé',
    className: 'booked',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
    svgIconFilename: 'ico-status-booked',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    className: 'reimbursed',
    dateFormat: FORMAT_DD_MM_YYYY,
    svgIconFilename: 'ico-status-reimbursed',
  },
]

function getBookingStatusDisplayInformations(bookingStatus) {
  return BOOKING_STATUS_DISPLAY_INFORMATIONS.find(({ id }) => bookingStatus.toLowerCase() === id)
}

export const computeHistoryClassName = bookingStatus => {
  const bookingStatusDisplayInformations = getBookingStatusDisplayInformations(bookingStatus)
  return `bs-history-${bookingStatusDisplayInformations.className}`
}

export const computeStatusClassName = bookingStatus => {
  const bookingStatusDisplayInformations = getBookingStatusDisplayInformations(bookingStatus)
  return `booking-status-${bookingStatusDisplayInformations.className}`
}

export const getStatusName = bookingStatus => {
  const bookingStatusDisplayInformations = getBookingStatusDisplayInformations(bookingStatus)
  return bookingStatusDisplayInformations.status
}

export const getStatusSVGIconFilename = bookingStatus => {
  const bookingStatusDisplayInformations = getBookingStatusDisplayInformations(bookingStatus)
  return bookingStatusDisplayInformations.svgIconFilename
}

export const getStatusDateFormat = bookingStatus => {
  const bookingStatusDisplayInformations = getBookingStatusDisplayInformations(bookingStatus)
  return bookingStatusDisplayInformations.dateFormat
}
