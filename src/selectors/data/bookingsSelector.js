import moment from 'moment'
import { createSelector } from 'reselect'

import selectStockById from '../selectStockById'
import selectOfferById from '../selectOfferById'
import { selectOffers } from './offersSelector'
import { selectStocks } from './stocksSelector'
import { dateStringPlusTimeZone } from '../../utils/date/date'

const SLIDING_DAYS = 8

export const selectBookings = state => state.data.bookings

export const selectBookingsOrderedByBeginningDateTimeAsc = createSelector(
  selectStocks,
  selectOffers,
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
  selectOffers,
  selectStocks,
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
  selectOffers,
  selectStocks,
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
  selectOffers,
  selectStocks,
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
