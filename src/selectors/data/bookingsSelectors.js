import moment from 'moment'
import createCachedSelector from 're-reselect'
import { createSelector } from 'reselect'

import filterPassedBookingLimitDatetimeStocks from '../../utils/filterPassedBookingLimitDatetimeStocks'
import { markAsCancelled } from '../../utils/markAsCancelled'
import { markAsBooked } from '../../utils/markBookingsAsBooked'
import { addModifierString } from '../../utils/addModifierString'
import filterRemainingStocks from '../../utils/filterRemainingStocks'
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

export const selectEventBookingsOfTheWeek = createSelector(
  selectBookings,
  state => state.data.offers,
  state => state.data.stocks,
  (bookings, offers, stocks) => {
    const now = moment()
    const sevenDaysFromNow = now.clone().add(SLIDING_DAYS, 'days')

    const filteredBookings = bookings.filter(booking => {
      if (booking.isCancelled) return false

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

export const selectFinishedEventBookings = createSelector(
  selectBookings,
  state => state.data.offers,
  state => state.data.stocks,
  (bookings, offers, stocks) =>
    bookings.filter(booking => {
      const filteredStock = selectStockById({ data: { stocks } }, booking.stockId)
      const filteredOffer = selectOfferById({ data: { offers } }, filteredStock.offerId)

      return (
        filteredOffer.isEvent &&
        !booking.isCancelled &&
        (filteredOffer.hasBookingLimitDatetimesPassed || booking.isEventExpired)
      )
    })
)

export const selectCancelledBookings = createSelector(
  selectBookings,
  bookings => bookings.filter(booking => booking.isCancelled)
)

export const selectUsedThingBookings = createSelector(
  selectBookings,
  state => state.data.stocks,
  (bookings, stocks) =>
    bookings.filter(booking => {
      const stock = selectStockById({ data: { stocks } }, booking.stockId)
      return !stock.beginningDatetime ? booking.isUsed : false
    })
)

export const selectFirstMatchingBookingByOfferId = createCachedSelector(
  selectBookings,
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
  selectBookings,
  (state, bookingId) => bookingId,
  (bookings, bookingId) => bookings.find(booking => booking.id === bookingId)
)((state, bookingId = '') => bookingId)

export const selectBookingByRouterMatch = createCachedSelector(
  selectBookings,
  state => state.data.stocks,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectOfferById(state, match.params.offerId),
  (bookings, allStocks, booking, offer) => {
    if (booking) return booking

    if (offer) {
      const stocks = selectStocksByOfferId({ data: { stocks: allStocks } }, offer.id)
      return selectFirstMatchingBookingByOfferId(
        {
          data: { bookings, stocks },
        },
        offer.id
      )
    }
  }
)((state, match) => {
  const { params } = match
  const { bookingId, mediationId, offerId } = params
  return `${bookingId || ' '}${mediationId || ' '}${offerId || ' '}`
})

export const selectBookables = createCachedSelector(
  selectBookings,
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

export const selectBookablesWithoutNotAvailableDate = createCachedSelector(
  selectBookings,
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
