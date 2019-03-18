import moment from 'moment'
import get from 'lodash.get'
import omit from 'lodash.omit'
import pick from 'lodash.pick'
import cloneDeep from 'lodash.clonedeep'
import createCachedSelector from 're-reselect'

import { pipe } from '../utils/functionnals'
import { isEmpty, isString } from '../utils/strings'
import { filterAvailableStocks } from '../helpers'

const MODIFIER_STRING_ID = 'selectBookables'

// ajoute une 'id' dans l'objet pour indiquer
// le selecteur qui a modifié les objets utilisables par une vue
export const addModifierString = () => items =>
  items.map(obj => ({
    ...obj,
    __modifiers__: (obj.__modifiers__ || []).concat([MODIFIER_STRING_ID]),
  }))

export const mapStockToBookable = timezone => stocks =>
  stocks.map(stock => {
    let extend
    if (stock.eventOccurrence) {
      extend = pick(stock.eventOccurrence, ['endDatetime', 'offerId'])
      extend.beginningDatetime = moment(
        stock.eventOccurrence.beginningDatetime
      ).tz(timezone)
    } else {
      extend = pick(stock, ['offerId'])
    }
    const base = omit(stock, ['eventOccurrence'])
    return Object.assign({}, base, extend)
  })

export const humanizeBeginningDate = () => items => {
  const format = 'dddd DD/MM/YYYY à HH:mm'
  return items.map(obj => {
    let date = obj.beginningDatetime || null
    const ismoment = date && moment.isMoment(date)
    const isstring = date && isString(date) && !isEmpty(date)
    const isvaliddate =
      isstring && moment(date, moment.ISO_8601, true).isValid()
    const isvalid = isvaliddate || ismoment
    if (!isvalid) return obj
    if (isstring) date = moment(date)
    const humanBeginningDate = date.format(format)
    return Object.assign({}, obj, { humanBeginningDate })
  })
}

export const markAsReserved = bookings => {
  const bookingsStockIds = bookings.map(({ stockId }) => stockId)
  return items =>
    items.map(obj => {
      const isReserved = (bookingsStockIds || []).includes(obj.id)
      return Object.assign({}, obj, {
        userAsAlreadyReservedThisDate: isReserved,
      })
    })
}

export const sortByDate = () => items =>
  items.sort((a, b) => {
    const datea = a.beginningDatetime
    const dateb = b.beginningDatetime
    if (!datea || !dateb) return 0
    if (datea.isAfter(dateb)) return 1
    if (datea.isAfter(dateb)) return -1
    return 0
  })

export const selectBookables = createCachedSelector(
  state => state.data.bookings,
  (state, recommendation) => recommendation,
  (bookings, recommendation) => {
    let stocks = get(recommendation, 'offer.stocks')
    // stocks = [stocks[0]]
    // NOTE -> prevents state to be mutated
    stocks = (stocks && cloneDeep(stocks)) || null
    if (!stocks || !stocks.length) return []
    const tz = get(recommendation, 'tz')
    return pipe(
      filterAvailableStocks,
      mapStockToBookable(tz),
      humanizeBeginningDate(),
      markAsReserved(bookings),
      addModifierString(),
      sortByDate()
    )(stocks)
  }
)((state, recommendation, match) => match.url)

export default selectBookables
