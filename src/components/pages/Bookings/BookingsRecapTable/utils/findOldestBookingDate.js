import { EMPTY_FILTER_VALUE } from '../Filters/_constants'

const findOldestBookingDate = bookingsRecap => {
  if (bookingsRecap.length > 0) {
    return bookingsRecap[bookingsRecap.length - 1].booking_date
  }
  return EMPTY_FILTER_VALUE
}

export default findOldestBookingDate
