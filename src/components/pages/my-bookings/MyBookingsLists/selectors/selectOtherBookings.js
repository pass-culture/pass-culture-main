import moment from 'moment'
import { createSelector } from 'reselect'

import selectStockById from '../../../../../selectors/selectStockById'
import selectValidBookings from '../../selectors/selectValidBookings'

export const filterBookingsInMoreThanTwoDaysOrPast = (stocks, bookings, now) => {
  const nowMoment = now || moment()
  const twoDaysFromNow = nowMoment.clone().add(2, 'days')
  const filteredBookings = bookings.filter(booking => {
    const stock = selectStockById({ data: { stocks } }, booking.stockId)
    const date = stock.beginningDatetime
    const hasBeginningDatetime = Boolean(date)
    const isBeforeNow = moment(date).isBefore(nowMoment)
    const isAfterTwoDays = moment(date).isAfter(twoDaysFromNow)
    return !hasBeginningDatetime || isAfterTwoDays || isBeforeNow
  })
  return filteredBookings
}

const selectOtherBookings = createSelector(
  state => state.data.stocks,
  selectValidBookings,
  (stocks, validBookings) => filterBookingsInMoreThanTwoDaysOrPast(stocks, validBookings)
)

export default selectOtherBookings
