import moment from 'moment'
import createCachedSelector from 're-reselect'

import {
  DEFAULT_BEGINNING_DATE_TIME_HOURS,
  DEFAULT_BEGINNING_DATE_TIME_MINUTES,
  getDatetimeOneDayAfter,
  getDatetimeAtSpecificHoursAndMinutes,
} from '../utils/utils'
import { selectStocksByOfferId } from '../../../../../../selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../../selectors/data/offersSelectors'

function mapArgsToCacheKey(state, stock, offerId, offererId) {
  return `${(stock && stock.id) || ''}${offerId || ''}/${offererId || ''}`
}

const selectFormInitialValuesByStockAndOfferIdAndOffererId = createCachedSelector(
  (state, stock) => stock,
  (state, stock, offerId) => selectOfferById(state, offerId),
  (state, stock, offerId) => selectStocksByOfferId(state, offerId),
  (state, stock, offerId) => offerId,
  (state, stock, offerId, offererId) => offererId,
  (state, stock, offerId, offererId, timezone) => timezone,
  (stock, offer, stocks, offerId, offererId, timezone) => {
    let { available, beginningDatetime, bookingLimitDatetime, id, price } = stock || {}

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
        : getDatetimeAtSpecificHoursAndMinutes(
            getDatetimeOneDayAfter(moment()),
            DEFAULT_BEGINNING_DATE_TIME_HOURS,
            DEFAULT_BEGINNING_DATE_TIME_MINUTES,
            timezone
          )
    }

    if (offer.isEvent && bookingLimitDatetime == null) {
      bookingLimitDatetime = ''
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
      Object.assign(formInitialValues, { beginningDatetime })
    }

    return formInitialValues
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByStockAndOfferIdAndOffererId
