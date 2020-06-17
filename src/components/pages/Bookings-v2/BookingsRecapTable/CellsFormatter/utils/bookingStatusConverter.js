const BOOKING_STATUS = [
  {
    id: 'validated',
    status: 'validé',
    className: 'validated',
    title: 'Validé',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    className: 'cancelled',
    title: 'Annulé',
  },
  {
    id: 'booked',
    status: 'réservé',
    className: 'booked',
    title: 'Réservé',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    className: 'reimbursed',
    title: 'Remboursé',
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

export const computeHistoryTitle = bookingStatusDisplayInformations => {
  const bookingStatus = getBookingStatusDisplayInformationsOrDefault(bookingStatusDisplayInformations)
  return bookingStatus.title
}

export const computeHistoryClassName = bookingStatusDisplayInformations => {
  return `bs-history-datetime-${bookingStatusDisplayInformations.className}`
}
