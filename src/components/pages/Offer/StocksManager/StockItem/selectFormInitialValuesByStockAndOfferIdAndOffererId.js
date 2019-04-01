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

    if (offer.eventId) {
      if (!beginningDatetime) {
        if (lastStock) {
          beginningDatetime = getDatetimeOneDayAfter(
            lastStock.beginningDatetime
          )
        } else {
          beginningDatetime = getDatetimeOneDayAfter(moment())
        }
      }

      if (!endDatetime) {
        if (lastStock) {
          endDatetime = getDatetimeOneDayAfter(lastStock.endDatetime)
        } else if (beginningDatetime) {
          endDatetime = getDatetimeOneHourAfter(beginningDatetime)
        }
      }
    }

    if (!bookingLimitDatetime) {
      bookingLimitDatetime = getDatetimeTwoDaysBefore(beginningDatetime)
    }

    if (typeof price === 'undefined') {
      if (lastStock) {
        price = lastStock.price
      } else {
        price = 0
      }
    }

    if (typeof available === 'undefined') {
      if (lastStock) {
        available = lastStock.available
      }
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
