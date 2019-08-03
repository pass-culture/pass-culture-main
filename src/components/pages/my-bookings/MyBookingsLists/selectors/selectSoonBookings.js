import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectValidBookings from '../../selectors/selectValidBookings'

export const filterBookingsInLessThanTwoDays = (bookings, now = null) => {
  const nowMoment = now || moment()
  const twoDaysFromNow = nowMoment.clone().add(2, 'days')
  const filteredBookings = bookings.filter(booking => {
    const date = get(booking, 'stock.beginningDatetime')
    const hasBeginningDatetime = Boolean(date)
    const isAfterNow = moment(date).isSameOrAfter(nowMoment)
    const isBeforeTwoDays = moment(date).isSameOrBefore(twoDaysFromNow)
    return hasBeginningDatetime && isBeforeTwoDays && isAfterNow
  })
  return filteredBookings
}

export const selectSoonBookings = createSelector(
  selectValidBookings,
  validBookings => filterBookingsInLessThanTwoDays(validBookings)
)

export default selectSoonBookings
