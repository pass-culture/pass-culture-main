import moment from 'moment'
import 'moment-timezone'

import { BOOKING_LIMIT_DATETIME_HOURS, BOOKING_LIMIT_DATETIME_MINUTES } from '../utils/utils'

const updateBookingLimitDatetime = ({
  beginningDatetime,
  bookingLimitDatetime,
  isEvent,
  previousBeginningDatetime,
  previousBookingLimitDatetime,
  timezone,
}) => {
  const bookingLimitDatetimeMoment = moment(bookingLimitDatetime)
  if (!isEvent || bookingLimitDatetimeMoment.isBefore(beginningDatetime, 'day')) {
    let nextBookingLimitDatetimeMoment = bookingLimitDatetimeMoment
    if (timezone) {
      nextBookingLimitDatetimeMoment = bookingLimitDatetimeMoment.tz(timezone)
    }
    const nextBookingLimitDatetime = nextBookingLimitDatetimeMoment
      .hours(BOOKING_LIMIT_DATETIME_HOURS)
      .minutes(BOOKING_LIMIT_DATETIME_MINUTES)
      .toISOString()
    return { bookingLimitDatetime: nextBookingLimitDatetime }
  }

  if (isEvent && bookingLimitDatetimeMoment.isSame(beginningDatetime, 'day')) {
    if (!previousBookingLimitDatetime || !previousBookingLimitDatetime) {
      return {}
    }
    const previousBookingLimitDatetimeMoment = moment(previousBookingLimitDatetime)
    if (previousBookingLimitDatetimeMoment.isBefore(previousBeginningDatetime, 'day')) {
      return { bookingLimitDatetime: beginningDatetime }
    }
    return {}
  }

  return { bookingLimitDatetime: beginningDatetime }
}

export default updateBookingLimitDatetime
