import createDecorator from 'final-form-calculate'
import createCachedSelector from 're-reselect'

import updateBookingLimitDatetime from './updateBookingLimitDatetime'

const mapArgsToCacheKey = ({ isEvent, timezone }) => `${isEvent || ''} ${timezone || ''}`

const adaptBookingLimitDatetimeGivenBeginningDatetime = createCachedSelector(
  ({ isEvent }) => isEvent,
  ({ timezone }) => timezone,
  (isEvent, timezone) =>
    createDecorator(
      {
        field: 'bookingLimitDatetime',
        updates: (
          bookingLimitDatetime,
          fieldName,
          { beginningDatetime },
          {
            beginningDatetime: previousBeginningDatetime,
            bookingLimitDatetime: previousBookingLimitDatetime,
          }
        ) =>
          updateBookingLimitDatetime({
            isEvent,
            beginningDatetime,
            bookingLimitDatetime,
            previousBeginningDatetime,
            previousBookingLimitDatetime,
            timezone,
          }),
      },
      {
        field: 'beginningDatetime',
        updates: (
          beginningDatetime,
          fieldName,
          { bookingLimitDatetime },
          {
            beginningDatetime: previousBeginningDatetime,
            bookingLimitDatetime: previousBookingLimitDatetime,
          }
        ) =>
          updateBookingLimitDatetime({
            beginningDatetime: beginningDatetime,
            bookingLimitDatetime: bookingLimitDatetime,
            isEvent,
            previousBeginningDatetime,
            previousBookingLimitDatetime,
            timezone,
          }),
      }
    )
)(mapArgsToCacheKey)

export default adaptBookingLimitDatetimeGivenBeginningDatetime
