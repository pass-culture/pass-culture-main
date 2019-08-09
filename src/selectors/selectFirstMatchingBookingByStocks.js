import createCachedSelector from 're-reselect'
import moment from 'moment'

function mapArgsToCacheKey(state, stocks) {
  return (stocks || []).map(s => s.id).join(' ')
}

export const selectFirstMatchingBookingByStocks = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (bookings, stocks) => {
    if (stocks.length === 0) {
      return null
    }

    stocks.sort((s1, s2) => {
      return moment(s1.beginningDateTime).diff(moment(s2.beginningDateTime))
    })

    for (let i in stocks) {
      let stock = stocks[i]

      if (moment(stock.beginningDateTime).isBefore(moment())) {
        continue
      }

      for (let j in bookings) {
        let booking = bookings[j]
        if (booking.stockId === stock.id && !booking.isCancelled) {
          return booking
        }
      }
    }

    return null
  }
)(mapArgsToCacheKey)

export default selectFirstMatchingBookingByStocks
