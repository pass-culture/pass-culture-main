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

const adaptBookingLimitDateTimeGivenBeginningDateTime = createCachedSelector(
  ({ isEvent }) => isEvent,
  isEvent =>
    createDecorator(
      {
        field: 'bookingLimitDatetime',
        updates: (bookingLimitDatetime, fieldName, allValues) => {
          const { beginningDatetime } = allValues
          const bookingLimitDatetimeMoment = moment(bookingLimitDatetime)

          if (
            !isEvent ||
            bookingLimitDatetimeMoment.isBefore(beginningDatetime, 'day')
          ) {
            const updatedDateTime = bookingLimitDatetimeMoment
              .hours(BOOKING_LIMIT_DATETIME_HOURS)
              .minutes(BOOKING_LIMIT_DATETIME_MINUTES)
              .toISOString(true)

            return {
              bookingLimitDatetime: updatedDateTime,
            }
          }

          return {
            bookingLimitDatetime: beginningDatetime,
          }
        },
      },
      {
        field: 'beginningDatetime',
        updates: (beginningDatetime, fieldName, allValues) => {
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
        },
      }
    )
)(mapArgsToCacheKey)

export default adaptBookingLimitDateTimeGivenBeginningDateTime
