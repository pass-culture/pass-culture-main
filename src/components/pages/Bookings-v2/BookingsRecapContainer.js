import { compose } from 'redux'

import BookingsRecap from '../Bookings-v2/BookingsRecap'
import { withRequiredLogin } from '../../hocs'
import { API_URL } from '../../../utils/config'

function duplicateDuoBookings(bookingRecaps) {
  return bookingRecaps
    .map(bookingRecap =>
      bookingRecap.booking_is_duo ? [bookingRecap, bookingRecap] : bookingRecap
    )
    .reduce((accumulator, currentValue) => accumulator.concat(currentValue), [])
}

export const fetchAllBookingsRecap = handleSuccess => {
  return fetch(`${API_URL}/bookings/pro`, { credentials: 'include' })
    .then(response => response.json())
    .then(duplicateDuoBookings)
    .then(handleSuccess)
}

export default compose(withRequiredLogin)(BookingsRecap)
