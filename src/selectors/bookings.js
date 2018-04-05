import get from 'lodash.get';
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.bookings,
  (bookings=[]) => {
    const twoDaysFromNow = new Date(new Date().getTime() + (2 * 24 * 60 * 60 * 1000));
    return bookings.reduce((result, booking) => {
      const isSoon = get(booking, 'eventOccurence.beginningDatetime') < twoDaysFromNow;
      return {
        soonBookings: result.soonBookings.concat(isSoon ? booking : []),
        otherBookings: result.otherBookings.concat(isSoon ? [] : booking),
      }
    }, {soonBookings: [], otherBookings: []})
  }
)
