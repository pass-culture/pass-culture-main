import moment from 'moment'
import isString from '../../utils/strings/isString'
import isEmpty from '../../utils/strings/isEmpty'
import createCachedSelector from 're-reselect'
import { selectStocksByOfferId } from './stocksSelectors'
import get from 'lodash.get'
import { getTimezone } from '../../utils/timezone'
import { pipe } from '../../utils/functionnals'
import filterAvailableStocks from '../../helpers/filterAvailableStocks'
import { selectOfferByRouterMatch } from './offersSelectors'
import { selectMediationByRouterMatch } from './mediationSelectors'
import { selectBookingByRouterMatch } from './bookingsSelectors'
import getIsNotBookable from '../../helpers/getIsNotBookable'

const MODIFIER_STRING_ID = 'selectBookables'

const antechronologicalSort = (a, b) => {
  const datea = moment(a.dateCreated)
  const dateb = moment(b.dateCreated)
  if (!datea || !dateb) return 0
  if (datea.isAfter(dateb)) return -1
  if (datea.isBefore(dateb)) return 1
  return 0
}

// ajoute une 'id' dans l'objet pour indiquer
// le selecteur qui a modifié les objets utilisables par une vue
export const addModifierString = () => items =>
  items.map(obj => ({
    ...obj,
    __modifiers__: (obj.__modifiers__ || []).concat([MODIFIER_STRING_ID]),
  }))
export const setTimezoneOnBeginningDatetime = timezone => stocks =>
  stocks.map(stock => {
    let extend = {}
    if (stock.beginningDatetime) {
      const dateWithTimezone = moment(stock.beginningDatetime).tz(timezone)
      extend = { beginningDatetime: dateWithTimezone }
    }
    return Object.assign({}, stock, extend)
  })
export const humanizeBeginningDate = () => items => {
  const format = 'dddd DD/MM/YYYY à HH:mm'
  return items.map(obj => {
    let date = obj.beginningDatetime || null
    const ismoment = date && moment.isMoment(date)
    const isstring = date && isString(date) && !isEmpty(date)
    const isvaliddate = isstring && moment(date, moment.ISO_8601, true).isValid()
    const isvalid = isvaliddate || ismoment
    if (!isvalid) return obj
    if (isstring) date = moment(date)
    const humanBeginningDate = date.format(format)
    return Object.assign({}, obj, { humanBeginningDate })
  })
}
export const markAsBooked = bookings => {
  const bookingsStockIds = bookings.map(({ stockId }) => stockId)
  return items =>
    items.map(obj => {
      const isBooked = (bookingsStockIds || []).includes(obj.id)
      return Object.assign({}, obj, {
        userHasAlreadyBookedThisDate: isBooked,
      })
    })
}
export const markAsCancelled = bookings => items =>
  items.map(item => {
    const sortedMatchingBookings = bookings
      .sort(antechronologicalSort)
      .find(booking => booking.stockId === item.id)
    const userHasCancelledThisDate =
      (sortedMatchingBookings && sortedMatchingBookings.isCancelled) || false
    return { ...item, userHasCancelledThisDate }
  })
export const sortByDate = () => items =>
  items.sort((a, b) => {
    const datea = a.beginningDatetime
    const dateb = b.beginningDatetime
    if (!datea || !dateb) return 0
    if (datea.isAfter(dateb)) return 1
    if (datea.isBefore(dateb)) return -1
    return 0
  })
export const selectBookables = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, offer) => offer,
  (bookings, allStocks, offer) => {
    let { venue } = offer || {}
    const stocks = selectStocksByOfferId({ data: { stocks: allStocks } }, get(offer, 'id'))
    const { departementCode } = venue || {}
    const tz = getTimezone(departementCode)

    if (!stocks || !stocks.length) return []

    return pipe(
      filterAvailableStocks,
      setTimezoneOnBeginningDatetime(tz),
      humanizeBeginningDate(),
      markAsBooked(bookings),
      markAsCancelled(bookings),
      addModifierString(),
      sortByDate()
    )(stocks)
  }
)((state, offer) => {
  const key = (offer && offer.id) || ' '
  return key
})

export const selectIsNotBookableByRouterMatch = createCachedSelector(
  selectOfferByRouterMatch,
  selectMediationByRouterMatch,
  selectBookingByRouterMatch,
  getIsNotBookable
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
})
