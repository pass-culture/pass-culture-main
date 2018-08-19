import moment from 'moment'
import get from 'lodash.get'
import createCachedSelector from 're-reselect'

export const filterByQuantity = recommendation => {
  const stocks = get(recommendation, 'offer.stocks')
  if (!stocks) return []
  // available > 0
  const filtered = stocks.filter(o => o.available && o.available > 0)
  return filtered
}

export const filterAvailableStocks = (stocks, now, tz) => {
  const results = stocks.filter(o => {
    const date = moment(o.bookingLimitDatetime).tz(tz)
    // - booking date limit >= now
    // FIXME -> minute ou heure ?
    const isSameOrAfterNow = date.isSameOrAfter(now, 'day')
    if (!isSameOrAfterNow) return false
    return true
  })
  return results
}

// transforme les dates en objets
// pour pouvoir faire le mapping entre une date, un prix, un horaire
// compose une map d'objet de type stock
// contenant les infos pour envoyer au service de booking
// FIXME -> regroupement des horaires pour un même jour
export const filteredToBookable = stocks =>
  stocks.map((stock, index) => {
    const eventOccurrence = stock.eventOccurrence || {}
    return {
      available: stock.available,
      beginningDatetime: eventOccurrence.beginningDatetime,
      endDatetime: eventOccurrence.endDatetime,
      eventOccurrenceId: eventOccurrence.id,
      index,
      limitDate: stock.bookingLimitDatetime,
      offerId: stock.eventOccurrence.offerId,
      price: stock.price,
      stockId: stock.id,
    }
  })

export const selectBookable = createCachedSelector(
  (state, recommendation) => recommendation,
  recommendation => {
    const stocks = filterByQuantity(recommendation)
    if (!stocks) return []
    const tz = get(recommendation, 'tz')
    /* <-------- DEBUG -------- */
    // const now = moment().tz(tz)
    const now = moment('2018-08-12T23:59:00Z').tz(tz)
    /* --------> */
    const filtered = filterAvailableStocks(stocks, now, tz)
    const bookables = filteredToBookable(filtered)
    /* <-------- DEBUG -------- */
    const last = Object.assign({}, bookables[bookables.length - 1], {
      beginningDatetime: '2018-08-18T10:00:00Z',
      price: 1234567890.12345678901234567890123456789,
      stockId: 'BWVA',
    })
    return bookables.concat([last])
    /* --------> */
    // return bookables
  }
)(
  // cached key
  (state, recommendation, match) => match.url
)

export default selectBookable
