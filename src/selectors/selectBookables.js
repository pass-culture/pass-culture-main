import moment from 'moment'
import get from 'lodash.get'
import omit from 'lodash.omit'
import pick from 'lodash.pick'
import cloneDeep from 'lodash.clonedeep'
import createCachedSelector from 're-reselect'

import { pipe } from '../utils/functionnals'
import { filterAvailableStocks } from '../helpers/filterAvailableStocks'

// eslint-disable-next-line
const { assert } = require('chai')

const MODIFIER_STRING_ID = 'selectBookables'

// ajoute une 'id' dans l'objet pour indiquer
// le selecteur qui a modifié les objets utilisables par une vue
export const addModifierString = () => items =>
  items.map(obj => ({
    ...obj,
    __modifiers__: (obj.__modifiers__ || []).concat([MODIFIER_STRING_ID]),
  }))

export const mapStockToBookable = timezone => items =>
  items.map(obj => {
    let extend
    if (obj.eventOccurence) {
      extend = pick(obj.eventOccurrence, ['endDatetime', 'offerId'])
      extend.beginningDatetime = moment(
        obj.eventOccurrence.beginningDatetime
      ).tz(timezone)
    } else {
      extend = pick(obj, ['offerId'])
    }
    const base = omit(obj, ['eventOccurrence'])
    return Object.assign({}, base, extend)
  })

export const humanizeBeginningDate = () => items =>
  // ajoute une date pré-formatée lisible par l'user
  items.map(obj =>
    Object.assign(
      {},
      obj,
      obj.beginningDatetime && {
        humanBeginningDate: obj.beginningDatetime.format(
          'dddd DD/MM/YYYY à HH:mm'
        ),
      }
    )
  )

export const markAsReserved = bookings => {
  const bookingsStockIds = bookings.map(({ stockId }) => stockId)
  // ajoute une information si l'utilisateur a déjà réservé cette offre
  return items =>
    items.map(obj => {
      const isReserved = (bookingsStockIds || []).includes(obj.id)
      return Object.assign({}, obj, {
        userAsAlreadyReservedThisDate: isReserved,
      })
    })
}

export const sortByDate = () => items =>
  // trie par ordre ASC les résultats
  items.sort((a, b) => {
    const datea = a.beginningDatetime
    const dateb = b.beginningDatetime
    if (datea.isAfter(dateb)) return 1
    if (datea.isAfter(dateb)) return -1
    return 0
  })

export const selectBookables = createCachedSelector(
  state => state.data.bookings,
  (state, recommendation) => recommendation,
  (bookings, recommendation) => {
    let stocks = get(recommendation, 'offer.stocks')
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
)(
  // cached key
  (state, recommendation, match) => match.url
)

export default selectBookables
