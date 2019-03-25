import moment from 'moment'
import createCachedSelector from 're-reselect'

import selectOfferById from 'selectors/selectOfferById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import { getDatetimeOneDayAfter, getDatetimeTwoDaysBefore } from './utils'

function mapArgsToCacheKey(state, stock, offerId, offererId) {
  return `${offerId || ''}/${offererId || ''}`
}

export const selectStockPatchByStockAndOfferIdAndOffererId = createCachedSelector(
  (state, stock) => stock,
  (state, stock, offerId) => selectOfferById(state, offerId),
  (state, stock, offerId) => selectStocksByOfferId(state, offerId),
  (state, stock, offerId) => offerId,
  (state, stock, offerId, offererId) => offererId,
  (stock, offer, stocks, offerId, offererId) => {
    let { beginningDatetime, bookingLimitDatetime, endDatetime, price } =
      stock || {}

    if (offer.eventId) {
      let lastStock
      if (stocks && stocks.length) {
        lastStock = stocks[0]
      }

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
          endDatetime = getDatetimeOneDayAfter()
        }
      }
    }

    if (!bookingLimitDatetime) {
      bookingLimitDatetime = getDatetimeTwoDaysBefore(beginningDatetime)
    }

    if (typeof price === 'undefined') {
      price = 0
    }

    return Object.assign(
      {
        beginningDatetime,
        bookingLimitDatetime,
        endDatetime,
        offerId,
        offererId,
        price,
      },
      stock
    )
  }
)(mapArgsToCacheKey)

export default selectStockPatchByStockAndOfferIdAndOffererId
