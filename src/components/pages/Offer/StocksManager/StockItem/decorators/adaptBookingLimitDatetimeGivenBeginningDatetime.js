import moment from 'moment'
import 'moment-timezone'

import createDecorator from 'final-form-calculate'
import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = ({ isEvent, timezone }) => `${isEvent || ''} ${timezone || ''}`

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

export const updateBookingLimitDatetime = ({
  beginningDatetime,
  bookingLimitDatetime,
  isEvent,
  timezone,
}) => {
  const bookingLimitDatetimeMoment = moment(bookingLimitDatetime)

  if (!isEvent) {
    if (bookingLimitDatetime && bookingLimitDatetimeMoment) {
      const nextBookingLimitDatetime = setBookingLimitDateTimeTo23h59(
        bookingLimitDatetimeMoment,
        timezone
      )
      return { bookingLimitDatetime: nextBookingLimitDatetime }
    } else {
      return { bookingLimitDatetime: null }
    }
  }

  if (isEvent && bookingLimitDatetimeMoment.isBefore(beginningDatetime, 'day')) {
    const nextBookingLimitDatetime = setBookingLimitDateTimeTo23h59(
      bookingLimitDatetimeMoment,
      timezone
    )
    return { bookingLimitDatetime: nextBookingLimitDatetime }
  }

  return { bookingLimitDatetime: beginningDatetime }
}

const adaptBookingLimitDatetimeGivenBeginningDatetime = createCachedSelector(
  ({ isEvent }) => isEvent,
  ({ timezone }) => timezone,
  (isEvent, timezone) =>
    createDecorator(
      {
        field: 'bookingLimitDatetime',
        updates: (bookingLimitDatetime, fieldName, { beginningDatetime }) =>
          updateBookingLimitDatetime({
            beginningDatetime,
            bookingLimitDatetime,
            isEvent,
            timezone,
          }),
      },
      {
        field: 'beginningDatetime',
        updates: (beginningDatetime, fieldName, { bookingLimitDatetime }) =>
          updateBookingLimitDatetime({
            beginningDatetime,
            bookingLimitDatetime,
            isEvent,
            timezone,
          }),
      }
    )
)(mapArgsToCacheKey)

export default adaptBookingLimitDatetimeGivenBeginningDatetime
