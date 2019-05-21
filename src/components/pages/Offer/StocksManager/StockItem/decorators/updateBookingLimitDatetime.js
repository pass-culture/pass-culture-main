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
}) => {
  const bookingLimitDatetimeMoment = moment(previousBookingLimitDatetime)

  if (
    !isEvent ||
    bookingLimitDatetimeMoment.isBefore(previousBeginningDatetime, 'day')
  ) {
    const updatedDateTime = bookingLimitDatetimeMoment
      .hours(BOOKING_LIMIT_DATETIME_HOURS)
      .minutes(BOOKING_LIMIT_DATETIME_MINUTES)
      .toISOString()

    return {
      bookingLimitDatetime: updatedDateTime,
    }
  }

  return {
    bookingLimitDatetime: previousBeginningDatetime,
  }
}

export default updateBookingLimitDatetime
