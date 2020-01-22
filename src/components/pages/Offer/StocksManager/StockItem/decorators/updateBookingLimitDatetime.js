import moment from 'moment'
import 'moment-timezone'

import { BOOKING_LIMIT_DATETIME_HOURS, BOOKING_LIMIT_DATETIME_MINUTES } from '../utils/utils'

const setBookingLimitDateTimeTo23h59 = (bookingLimitDatetimeMoment, timezone) => {
  let nextBookingLimitDatetimeMoment = bookingLimitDatetimeMoment

  if (timezone) {
    nextBookingLimitDatetimeMoment = bookingLimitDatetimeMoment.tz(timezone)
  }

  return nextBookingLimitDatetimeMoment
    .hours(BOOKING_LIMIT_DATETIME_HOURS)
    .minutes(BOOKING_LIMIT_DATETIME_MINUTES)
    .toISOString()
}

const updateBookingLimitDatetime = ({
  beginningDatetime,
  bookingLimitDatetime,
  isEvent,
  timezone,
}) => {

  const bookingLimitDatetimeMoment = moment(bookingLimitDatetime)

  if (!isEvent) {
    const nextBookingLimitDatetime = setBookingLimitDateTimeTo23h59(bookingLimitDatetimeMoment, timezone)
    return { bookingLimitDatetime: nextBookingLimitDatetime }
  }

  if (isEvent && bookingLimitDatetimeMoment.isBefore(beginningDatetime, 'day')) {
    const nextBookingLimitDatetime = setBookingLimitDateTimeTo23h59(bookingLimitDatetimeMoment, timezone)
    return { bookingLimitDatetime: nextBookingLimitDatetime }
  }

  return { bookingLimitDatetime: beginningDatetime }

}

export default updateBookingLimitDatetime
