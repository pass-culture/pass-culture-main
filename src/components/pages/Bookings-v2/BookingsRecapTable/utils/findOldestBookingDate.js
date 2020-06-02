const findOldestBookingDate = bookingsRecap => {
  if (bookingsRecap.length > 0) {
    return bookingsRecap[bookingsRecap.length - 1].booking_date
  }
  return null
}

export default findOldestBookingDate
