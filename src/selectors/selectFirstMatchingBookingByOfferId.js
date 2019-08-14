import createCachedSelector from 're-reselect'
import moment from 'moment'

const mapArgsToCacheKey = (state, offerId) => offerId || ''

export const selectFirstMatchingBookingByOfferId = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, offerId) => offerId,
  (bookings, stocks, offerId) => {
    if (stocks.length === 0) {
      return null
    }

    stocks.sort((s1, s2) => {
      return moment(s1.beginningDatetime).diff(moment(s2.beginningDatetime))
    })

    for (let i in stocks) {
      let stock = stocks[i]

      if (stock.offerId !== offerId || moment(stock.beginningDatetime).isBefore(moment())) {
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

export default selectFirstMatchingBookingByOfferId
