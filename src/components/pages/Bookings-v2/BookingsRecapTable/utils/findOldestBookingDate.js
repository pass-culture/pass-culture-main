const sortByOldestBookingDateFirst = (bookingRecap1, bookingRecap2) => {
  if (bookingRecap1.booking_date < bookingRecap2.booking_date) {
    return -1
  }
  if (bookingRecap1.booking_date > bookingRecap2.booking_date) {
    return 1
  }
  return 0
}

const findOldestBookingDate = bookingsRecap => {
  if (bookingsRecap.length > 0) {
    const sortedBookingsRecap = bookingsRecap.sort(sortByOldestBookingDateFirst)
    return sortedBookingsRecap[0].booking_date
  }
  return null
}

export default findOldestBookingDate
