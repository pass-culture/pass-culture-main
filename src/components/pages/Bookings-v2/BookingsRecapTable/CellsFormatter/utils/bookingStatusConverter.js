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

const BOOKING_HISTORY_DATETYPE = [
  {
    status: 'validated',
    historyDatetype: 'date_used',
  },
  {
    status: 'cancelled',
    historyDatetype: 'cancellation_date',
  },
  {
    status: 'booked',
    historyDatetype: 'booking_date',
  },
  {
    status: 'reimbursed',
    historyDatetype: 'payment_date',
  },
]

export const computeHistoryDatetypeToStatus = bookingHistoryDatetype => {
  const bookingStatusFound = BOOKING_HISTORY_DATETYPE.find(({ historyDatetype }) => bookingHistoryDatetype === historyDatetype)
  return bookingStatusFound ? bookingStatusFound : BOOKING_STATUS_DEFAULT
}

export const computeHistoryTitleFromStatus = bookingHistoryStatus => {
  const bookingStatusFound = BOOKING_STATUS.find(({ id }) => bookingHistoryStatus === id)
  return bookingStatusFound.status.charAt(0).toUpperCase()
}

export const computeBookingHistoryClassName = bookingHistoryDatetype => {
  return `bs-history-datetime-${computeHistoryDatetypeToStatus(bookingHistoryDatetype)}`
}
