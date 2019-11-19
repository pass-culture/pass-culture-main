import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'
import { createSelector } from 'reselect'

import filterAvailableStocks from '../../helpers/filterAvailableStocks'
import { markAsCancelled } from '../../helpers/markAsCancelled'
import { markAsBooked } from '../../helpers/markBookingsAsBooked'
import { addModifierString } from '../../utils/addModifierString'
import { dateStringPlusTimeZone } from '../../utils/date/date'
import { humanizeBeginningDateTime } from '../../utils/date/humanizeBeginningDateTime'
import { sortByDateChronologically } from '../../utils/date/sortByDateChronologically'
import { pipe } from '../../utils/functionnals'
import { getTimezone, setTimezoneOnBeginningDatetime } from '../../utils/timezone'
import { selectOfferById } from './offersSelectors'
import { selectStockById, selectStocksByOfferId } from './stocksSelectors'

const SLIDING_DAYS = 8

export const selectBookings = state => state.data.bookings

export const selectBookingsOrderedByBeginningDateTimeAsc = createSelector(
  state => state.data.stocks,
  state => state.data.offers,
  (state, bookings) => bookings,
  (stocks, offers, bookings) => {
    return bookings.sort((booking1, booking2) => {
      const permanent = null
      const timestampFormat = 'X'
      const stock1 = selectStockById({ data: { stocks } }, booking1.stockId)
      const stock2 = selectStockById({ data: { stocks } }, booking2.stockId)
      const offer1 = selectOfferById({ data: { offers } }, stock1.offerId)
      const offer2 = selectOfferById({ data: { offers } }, stock2.offerId)
      const timestampPlusTimeZone1 = dateStringPlusTimeZone(
        stock1.beginningDatetime,
        offer1.venue.departementCode
      )
      const timestampPlusTimeZone2 = dateStringPlusTimeZone(
        stock2.beginningDatetime,
        offer2.venue.departementCode
      )

      const date1 =
        stock1.beginningDatetime === permanent
          ? Infinity
          : moment(timestampPlusTimeZone1).format(timestampFormat)
      const date2 =
        stock2.beginningDatetime === permanent
          ? Infinity
          : moment(timestampPlusTimeZone2).format(timestampFormat)

      return date1 - date2
    })
  }
)

export const selectBookingsOfTheWeek = createSelector(
  selectBookings,
  state => state.data.offers,
  state => state.data.stocks,
  (bookings, offers, stocks) => {
    const now = moment()
    const sevenDaysFromNow = now.clone().add(SLIDING_DAYS, 'days')

    const filteredBookings = bookings.filter(booking => {
      if (booking.isCancelled || booking.isUsed) return false

      const stock = selectStockById({ data: { stocks } }, booking.stockId)
      const beginningDatetime = moment(stock.beginningDatetime)
      const isSameOrAfterNow = beginningDatetime.isSameOrAfter(now)
      const isSameOrBeforeSevenDays = beginningDatetime.isSameOrBefore(sevenDaysFromNow)

      return isSameOrBeforeSevenDays && isSameOrAfterNow
    })

    return selectBookingsOrderedByBeginningDateTimeAsc(
      { data: { offers, stocks } },
      filteredBookings
    )
  }
)

export const selectUpComingBookings = createSelector(
  selectBookings,
  state => state.data.offers,
  state => state.data.stocks,
  (bookings, offers, stocks) => {
    const sevenDaysFromNow = moment()
      .clone()
      .add(SLIDING_DAYS, 'days')

    const filteredBookings = bookings.filter(booking => {
      if (booking.isCancelled || booking.isUsed) return false

      const stock = selectStockById({ data: { stocks } }, booking.stockId)
      const isPermanent = stock.beginningDatetime === null
      const isAfterSevenDaysFromNow = moment(stock.beginningDatetime).isAfter(sevenDaysFromNow)

      return isPermanent || isAfterSevenDaysFromNow
    })

    return selectBookingsOrderedByBeginningDateTimeAsc(
      { data: { offers, stocks } },
      filteredBookings
    )
  }
)

export const selectFinishedBookings = createSelector(
  selectBookings,
  state => state.data.offers,
  state => state.data.stocks,
  (bookings, offers, stocks) =>
    bookings.filter(booking => {
      const filteredStock = selectStockById({ data: { stocks } }, booking.stockId)
      const filteredOffer = selectOfferById({ data: { offers } }, filteredStock.offerId)

      return !booking.isCancelled && (filteredOffer.isNotBookable || booking.isEventExpired)
    })
)

export const selectCancelledBookings = createSelector(
  selectBookings,
  bookings => bookings.filter(booking => booking.isCancelled)
)

export const selectUsedBookings = createSelector(
  state => state.data.bookings,
  bookings => bookings.filter(booking => booking.isUsed)
)

export const selectFirstMatchingBookingByOfferId = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, offerId) => offerId,
  (bookings, stocks, offerId) => {
    if (stocks.length === 0) {
      return null
    }

    stocks.sort((s1, s2) => {
      return moment(s1.beginningDatetime).diff(moment(s2.beginningDatetime))
    })

    for (let i in stocks) {
      let stock = stocks[i]

      if (stock.offerId !== offerId || moment(stock.beginningDatetime).isBefore(moment())) {
        continue
      }

      for (let j in bookings) {
        let booking = bookings[j]

        if (booking.stockId === stock.id && !booking.isCancelled) {
          return booking
        }
      }
    }

    return null
  }
)((state, offerId = '') => offerId)

export const selectBookingById = createCachedSelector(
  state => state.data.bookings,
  (state, bookingId) => bookingId,
  (bookings, bookingId) => bookings.find(booking => booking.id === bookingId)
)((state, bookingId = '') => bookingId)

export const selectBookingByRouterMatch = createCachedSelector(
  state => state.data.bookings,
  state => state.data.stocks,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectOfferById(state, match.params.offerId),
  (bookings, allStocks, booking, offer) => {
    if (booking) return booking

    if (offer) {
      const stocks = selectStocksByOfferId({ data: { stocks: allStocks } }, offer.id)
      const firstMatchingBooking = selectFirstMatchingBookingByOfferId(
        {
          data: { bookings, stocks },
        },
        offer.id
      )

      return firstMatchingBooking
    }
  }
)((state, match) => {
  const { params } = match
  const { bookingId, mediationId, offerId } = params
  return `${bookingId || ' '}${mediationId || ' '}${offerId || ' '}`
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
      humanizeBeginningDateTime(),
      markAsBooked(bookings),
      markAsCancelled(bookings),
      addModifierString(),
      sortByDateChronologically()
    )(stocks)
  }
)((state, offer) => {
  const key = (offer && offer.id) || ' '
  return key
})
