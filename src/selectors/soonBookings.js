import { createSelector } from 'reselect'

import bookingsSelector from './bookings'

export default createSelector(bookingsSelector, bookings =>
  bookings.filter(booking => booking.isSoon)
)
