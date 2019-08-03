import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, stocks) {
  return (stocks || []).map(s => s.id).join(' ')
}

export const selectFirstMatchingBookingByStocks = createCachedSelector(
  state => state.data.bookings,
  (state, stocks) => stocks && stocks.map(s => s.id),
  (bookings, stockIds) => {
    if (!stockIds) {
      return
    }
    const matchingBookings = bookings.filter(b => stockIds.includes(b.stockId))
    matchingBookings.sort((b1, b2) => {
      if (!b1.isCancelled && b2.isCancelled) {
        return -1
      } else if (b1.isCancelled && !b2.isCancelled) {
        return 1
      } else if (!b1.isCancelled && !b2.isCancelled) {
        return 0
      }
      return 0
    })
    const firstMatchingBooking = matchingBookings[0]
    return firstMatchingBooking
  }
)(mapArgsToCacheKey)

export default selectFirstMatchingBookingByStocks
