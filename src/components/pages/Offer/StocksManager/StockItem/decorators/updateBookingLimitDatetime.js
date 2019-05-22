import moment from 'moment'
import 'moment-timezone'

import {
  BOOKING_LIMIT_DATETIME_HOURS,
  BOOKING_LIMIT_DATETIME_MINUTES,
} from '../utils'

const updateBookingLimitDatetime = ({
  isEvent,
  previousBeginningDatetime,
  previousBookingLimitDatetime,
  timezone,
}) => {
  let bookingLimitDatetimeMoment = moment(previousBookingLimitDatetime).utc()

  if (
    !isEvent ||
    bookingLimitDatetimeMoment.isBefore(previousBeginningDatetime, 'day')
  ) {
    if (timezone) {
      bookingLimitDatetimeMoment = bookingLimitDatetimeMoment.tz(timezone)
    }
    return bookingLimitDatetimeMoment
      .hours(BOOKING_LIMIT_DATETIME_HOURS)
      .minutes(BOOKING_LIMIT_DATETIME_MINUTES)
      .toISOString()
  }

  return previousBeginningDatetime
}

export default updateBookingLimitDatetime
