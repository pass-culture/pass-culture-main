const BOOKING_STATUS = [
  {
    id: 'validated',
    status: 'validé',
    className: 'validated',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    className: 'cancelled',
  },
  {
    id: 'booked',
    status: 'réservé',
    className: 'booked',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    className: 'reimbursed',
  },
]

const BOOKING_STATUS_DEFAULT = {
  id: 'default',
  className: 'default',
}

export const getBookingStatusDisplayInformationsOrDefault = bookingStatusInfos => {
  const bookingStatusFound = BOOKING_STATUS.find(({ id }) => bookingStatusInfos === id)
  return bookingStatusFound ? bookingStatusFound : BOOKING_STATUS_DEFAULT
}

export const computeStatusClassName = bookingStatusDisplayInformations => {
  return `booking-status-${bookingStatusDisplayInformations.className}`
}
