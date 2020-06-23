import { FORMAT_DD_MM_YYYY, FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../../utils/date'

const BOOKING_STATUS = [
  {
    id: 'validated',
    status: 'validé',
    className: 'validated',
    title: 'Validé',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
  },
  {
    id: 'cancelled',
    status: 'annulé',
    className: 'cancelled',
    title: 'Annulé',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
  },
  {
    id: 'booked',
    status: 'réservé',
    className: 'booked',
    title: 'Réservé',
    dateFormat: FORMAT_DD_MM_YYYY_HH_mm,
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    className: 'reimbursed',
    title: 'Remboursé',
    dateFormat: FORMAT_DD_MM_YYYY,
  },
]

const BOOKING_STATUS_DEFAULT = {
  id: 'default',
  className: 'default',
}

export const computeHistoryClassName = bookingStatusDisplayInformations => {
  const bookingStatus = getBookingStatusDisplayInformationsOrDefault(
    bookingStatusDisplayInformations
  )
  return `bs-history-${bookingStatus.className}`
}

export const computeStatusClassName = bookingStatusDisplayInformations => {
  return `booking-status-${bookingStatusDisplayInformations.className}`
}

export const getBookingStatusDisplayInformationsOrDefault = bookingStatusInfos => {
  const bookingStatusFound = BOOKING_STATUS.find(({ id }) => bookingStatusInfos === id)
  return bookingStatusFound ? bookingStatusFound : BOOKING_STATUS_DEFAULT
}

export const getStatusTitle = bookingStatusDisplayInformations => {
  const bookingStatus = getBookingStatusDisplayInformationsOrDefault(
    bookingStatusDisplayInformations
  )
  return bookingStatus.title
}

export const getStatusDateFormat = bookingStatusDisplayInformations => {
  const bookingStatus = getBookingStatusDisplayInformationsOrDefault(
    bookingStatusDisplayInformations
  )
  return bookingStatus.dateFormat
}
