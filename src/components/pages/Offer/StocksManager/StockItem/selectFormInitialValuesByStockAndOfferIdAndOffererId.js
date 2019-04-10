import moment from 'moment'
import createCachedSelector from 're-reselect'

import selectOfferById from 'selectors/selectOfferById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import {
  getDatetimeOneDayAfter,
  getDatetimeOneHourAfter,
  getDatetimeTwoDaysBefore,
} from './utils'

function mapArgsToCacheKey(state, stock, offerId, offererId) {
  return `${(stock && stock.id) || ''}${offerId || ''}/${offererId || ''}`
}

export const selectFormInitialValuesByStockAndOfferIdAndOffererId = createCachedSelector(
  (state, stock) => stock,
  (state, stock, offerId) => selectOfferById(state, offerId),
  (state, stock, offerId) => selectStocksByOfferId(state, offerId),
  (state, stock, offerId) => offerId,
  (state, stock, offerId, offererId) => offererId,
  (stock, offer, stocks, offerId, offererId) => {
    let {
      available,
      beginningDatetime,
      bookingLimitDatetime,
      endDatetime,
      id,
      price,
    } = stock || {}

    if (!offer) {
      return {}
    }

    let lastStock
    if (stocks && stocks.length) {
      lastStock = stocks[0]
    }

    if (offer.eventId && !beginningDatetime) {
      beginningDatetime = lastStock
        ? getDatetimeOneDayAfter(lastStock.beginningDatetime)
        : getDatetimeOneDayAfter(moment())
    }

    if (offer.eventId && !endDatetime) {
      endDatetime = lastStock
        ? getDatetimeOneDayAfter(lastStock.endDatetime)
        : getDatetimeOneHourAfter(beginningDatetime)
    }

    if (!bookingLimitDatetime) {
      bookingLimitDatetime = getDatetimeTwoDaysBefore(beginningDatetime)
    }

    if (typeof price === 'undefined') {
      price = lastStock ? lastStock.price : 0
    } else if (price === 0) {
      price = ''
    }

    if (typeof available === 'undefined' && lastStock) {
      available = lastStock.available
    }

    return {
      available,
      beginningDatetime,
      bookingLimitDatetime,
      endDatetime,
      id,
      offerId,
      offererId,
      price,
    }
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByStockAndOfferIdAndOffererId
