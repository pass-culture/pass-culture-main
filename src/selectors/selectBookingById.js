import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, bookingId) {
  return bookingId || ''
}

export const selectBookingById = createCachedSelector(
  state => state.data.bookings,
  (state, bookingId) => bookingId,
  (bookings, bookingId) => bookings.find(booking => booking.id === bookingId)
)(mapArgsToCacheKey)

export default selectBookingById
