import moment from 'moment'
import get from 'lodash.get'
import omit from 'lodash.omit'
import pick from 'lodash.pick'
import cloneDeep from 'lodash.clonedeep'
import createCachedSelector from 're-reselect'

import { pipe } from '../utils/functionnals'

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

export const mapEventOccurenceToBookable = () => items =>
  items.map(obj => {
    const extend = pick(obj.eventOccurrence, [
      'beginningDatetime',
      'endDatetime',
      'offerId',
    ])
    const base = omit(obj, ['eventOccurrence'])
    return Object.assign({}, base, extend)
  })

export const humanizeBeginningDate = tz => items =>
  // ajoute une date pré-formatée lisible par l'user
  items.map(obj =>
    Object.assign({}, obj, {
      humanBeginningDate: moment(obj.beginningDatetime)
        .tz(tz)
        .format('dddd DD/MM/YYYY à HH:mm'),
    })
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

export const filterOutdated = (now, tz) => items => {
  const results = items.filter(o => {
    const date = moment(o.bookingLimitDatetime).tz(tz)
    // - booking date limit >= now
    // FIXME -> minute, heure ou jour ?
    const isSameOrAfterNow = date.isSameOrAfter(now, 'day')
    if (!isSameOrAfterNow) return false
    return true
  })
  return results
}

export const sortByDate = () => items =>
  // trie par ordre ASC les résultats
  items.sort((a, b) => {
    const datea = a.beginningDatetime
    const dateb = b.beginningDatetime
    if (datea > dateb) return 1
    if (datea < dateb) return -1
    return 0
  })

export const selectBookables = createCachedSelector(
  state => state.data.bookings,
  (state, recommendation) => recommendation,
  (bookings, recommendation) => {
    let stocks = get(recommendation, 'offer.stocks')
    // NOTE: cloneDeep -> prevents redux.state mutations
    stocks = (stocks && cloneDeep(stocks)) || null
    if (!stocks || !stocks.length) return []
    const tz = get(recommendation, 'tz')
    const now = moment().tz(tz)
    // DEBUG
    // const now = moment('2018-08-30T21:59:00Z').tz(tz)
    return pipe(
      filterOutdated(now, tz),
      mapEventOccurenceToBookable(),
      humanizeBeginningDate(tz),
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
