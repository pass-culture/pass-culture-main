import moment from 'moment'
import createCachedSelector from 're-reselect'

import selectOfferById from 'selectors/selectOfferById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import {
  BOOKING_LIMIT_DATETIME_HOURS,
  BOOKING_LIMIT_DATETIME_MINUTES,
  getDatetimeOneDayAfter,
  getDatetimeOneHourAfter,
  getDatetimeAtSpecificHoursAndMinutes,
} from '../utils'

function mapArgsToCacheKey(state, stock, offerId, offererId) {
  return `${(stock && stock.id) || ''}${offerId || ''}/${offererId || ''}`
}

// TODO No (green) tests found for this part of code
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

    if (offer.isEvent && !beginningDatetime) {
      beginningDatetime = lastStock
        ? getDatetimeOneDayAfter(lastStock.beginningDatetime)
        : getDatetimeOneDayAfter(moment())
    }

    if (offer.isEvent && !endDatetime) {
      // FIXME Should use the offer duration
      endDatetime = lastStock
        ? getDatetimeOneDayAfter(lastStock.endDatetime)
        : getDatetimeOneHourAfter(beginningDatetime)
    }

    if (beginningDatetime && !bookingLimitDatetime) {
      bookingLimitDatetime = getDatetimeAtSpecificHoursAndMinutes(
        beginningDatetime,
        BOOKING_LIMIT_DATETIME_HOURS,
        BOOKING_LIMIT_DATETIME_MINUTES
      )
    }

    if (typeof price === 'undefined') {
      price = lastStock ? lastStock.price : 0
    } else if (price === 0) {
      price = ''
    }

    if (typeof available === 'undefined' && lastStock) {
      available = lastStock.available
    }

    const formInitialValues = {
      available,
      bookingLimitDatetime,
      id,
      offerId,
      offererId,
      price,
    }

    if (offer.isEvent) {
      Object.assign(formInitialValues, { beginningDatetime, endDatetime })
    }

    return formInitialValues
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByStockAndOfferIdAndOffererId
