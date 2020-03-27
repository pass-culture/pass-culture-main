import createCachedSelector from 're-reselect'

import { selectOfferById } from './offersSelectors'
import { humanizeBeginningDateTime } from '../../utils/date/humanizeBeginningDateTime'
import { sortByDateChronologically } from '../../utils/date/sortByDateChronologically'
import { pipe } from '../../utils/functionnals'
import { getTimezone, setTimezoneOnBeginningDatetime } from '../../utils/timezone'
import filterPassedBookingLimitDatetimeStocks from '../../utils/filterPassedBookingLimitDatetimeStocks'
import { markAsCancelled } from '../../utils/markAsCancelled'
import { markAsBooked } from '../../utils/markBookingsAsBooked'
import { addModifierString } from '../../utils/addModifierString'
import filterRemainingStocks from '../../utils/filterRemainingStocks'

const selectStocks = state => state.data.stocks

export const selectStockById = createCachedSelector(
  selectStocks,
  (state, stockId) => stockId,
  (stocks, stockId) => stocks.find(stock => stock.id === stockId)
)((state, stockId = '') => stockId)

export const selectStocksByOfferId = createCachedSelector(
  selectStocks,
  (state, offerId) => offerId,
  (stocks, offerId) => stocks.filter(stock => stock.offerId === offerId)
)((state, offerId = '') => offerId)

export const selectIsEnoughStockForOfferDuo = createCachedSelector(
  (state, offerId) => offerId,
  selectStocksByOfferId,
  (offerId, stocks) => {
    const stocksAvailableForOfferDuo = stocks.filter(isAvailableForDuo)
    return stocksAvailableForOfferDuo.length > 0
  }
)((state, offerId) => offerId || '')

export const selectIsStockDuo = createCachedSelector(
  selectStockById,
  (state, stockId, offerId) => selectOfferById(state, offerId),
  (stock, offer) => {
    const isEnoughAvailable = isAvailableForDuo(stock)
    const isOfferDuo = offer && offer.isDuo
    const isStockDuo = isEnoughAvailable && isOfferDuo

    return isStockDuo
  }
)((state, stockId) => stockId || '')

const isAvailableForDuo = stock =>
  stock && (stock.remainingQuantity >= 2 || stock.remainingQuantity === 'unlimited')

export const selectBookables = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, offer) => offer,
  (bookings, allStocks, offer) => {
    let { venue } = offer || {}
    const stocks = selectStocksByOfferId({ data: { stocks: allStocks } }, offer && offer.id)
    const { departementCode } = venue || {}
    const tz = getTimezone(departementCode)

    if (!stocks || !stocks.length) return []

    return pipe(
      filterPassedBookingLimitDatetimeStocks,
      setTimezoneOnBeginningDatetime(tz),
      humanizeBeginningDateTime(),
      markAsBooked(bookings),
      markAsCancelled(bookings),
      addModifierString(),
      sortByDateChronologically()
    )(stocks)
  }
)((state, offer) => {
  return (offer && offer.id) || ' '
})

export const selectBookablesWithoutDateNotAvailable = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, offer) => offer,
  (bookings, allStocks, offer) => {
    let { venue } = offer || {}
    const stocks = selectStocksByOfferId({ data: { stocks: allStocks } }, offer && offer.id)
    const { departementCode } = venue || {}
    const tz = getTimezone(departementCode)

    if (!stocks || !stocks.length) return []

    return pipe(
      filterPassedBookingLimitDatetimeStocks,
      filterRemainingStocks,
      setTimezoneOnBeginningDatetime(tz),
      humanizeBeginningDateTime(),
      markAsBooked(bookings),
      markAsCancelled(bookings),
      addModifierString(),
      sortByDateChronologically()
    )(stocks)
  }
)((state, offer) => {
  return (offer && offer.id) || ' '
})
