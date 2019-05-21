import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'
import {
  BOOKING_LIMIT_DATETIME_HOURS,
  BOOKING_LIMIT_DATETIME_MINUTES,
} from '../utils'

const mapArgsToCacheKey = ({ isEvent, timezone }) =>
  `${isEvent || ''} ${timezone || ''}`

export const updateBookingLimitDatetime = (
  isEvent,
  bookingLimitDatetime,
  allValues
) => {
  const { beginningDatetime } = allValues
  const bookingLimitDatetimeMoment = moment(bookingLimitDatetime)

  if (
    !isEvent ||
    bookingLimitDatetimeMoment.isBefore(beginningDatetime, 'day')
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
    bookingLimitDatetime: beginningDatetime,
  }
}

export const updateBeginningDatetime = (
  isEvent,
  beginningDatetime,
  allValues
) => {
  const { bookingLimitDatetime } = allValues
  const bookingLimitDatetimeMoment = moment(bookingLimitDatetime)

  if (
    !isEvent ||
    bookingLimitDatetimeMoment.isBefore(beginningDatetime, 'day')
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
    bookingLimitDatetime: beginningDatetime,
  }
}

export const adaptBookingLimitDateTimeGivenBeginningDateTime = createCachedSelector(
  ({ isEvent }) => isEvent,
  isEvent =>
    createDecorator(
      {
        field: 'bookingLimitDatetime',
        updates: (beginningDatetime, fieldName, allValues) =>
          updateBookingLimitDatetime(isEvent, beginningDatetime, allValues),
      },
      {
        field: 'beginningDatetime',
        updates: (beginningDatetime, fieldName, allValues) =>
          updateBeginningDatetime(isEvent, beginningDatetime, allValues),
      }
    )
)(mapArgsToCacheKey)

export default adaptBookingLimitDateTimeGivenBeginningDateTime
