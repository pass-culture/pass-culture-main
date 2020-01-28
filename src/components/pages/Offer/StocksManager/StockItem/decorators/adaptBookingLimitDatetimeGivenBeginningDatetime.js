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
          { beginningDatetime }
        ) =>
          updateBookingLimitDatetime({
            beginningDatetime,
            bookingLimitDatetime,
            isEvent,
            timezone,
          }),
      },
      {
        field: 'beginningDatetime',
        updates: (
          beginningDatetime,
          fieldName,
          { bookingLimitDatetime }
        ) =>
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
