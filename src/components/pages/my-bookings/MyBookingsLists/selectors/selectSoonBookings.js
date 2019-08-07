import moment from 'moment'
import { createSelector } from 'reselect'

import selectStockById from '../../../../../selectors/selectStockById'
import selectValidBookings from '../../selectors/selectValidBookings'

export const filterBookingsInLessThanTwoDays = (stocks, bookings, now = null) => {
  const nowMoment = now || moment()
  const twoDaysFromNow = nowMoment.clone().add(2, 'days')
  const filteredBookings = bookings.filter(booking => {
    const stock = selectStockById({ data: { stocks } }, booking.stockId)
    const date = stock.beginningDatetime
    const hasBeginningDatetime = Boolean(date)
    const isAfterNow = moment(date).isSameOrAfter(nowMoment)
    const isBeforeTwoDays = moment(date).isSameOrBefore(twoDaysFromNow)
    return hasBeginningDatetime && isBeforeTwoDays && isAfterNow
  })
  return filteredBookings
}

export const selectSoonBookings = createSelector(
  state => state.data.stocks,
  selectValidBookings,
  (stocks, validBookings) => filterBookingsInLessThanTwoDays(stocks, validBookings)
)

export default selectSoonBookings
