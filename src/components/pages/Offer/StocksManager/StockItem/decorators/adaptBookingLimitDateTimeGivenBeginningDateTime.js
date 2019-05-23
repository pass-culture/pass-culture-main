import createDecorator from 'final-form-calculate'
import moment from 'moment'
import createCachedSelector from 're-reselect'

import updateBookingLimitDatetime from './updateBookingLimitDatetime'

const mapArgsToCacheKey = ({ isEvent, timezone }) =>
  `${isEvent || ''} ${timezone || ''}`

const adaptBookingLimitDatetimeGivenBeginningDatetime = createCachedSelector(
  ({ isEvent }) => isEvent,
  ({ timezone }) => timezone,
  (isEvent, timezone) =>
    createDecorator(
      {
        field: 'bookingLimitDatetime',
        updates: (bookingLimitDatetime, fieldName, { beginningDatetime }) => {
          if (
            moment(bookingLimitDatetime)
              .utc()
              .isSame(beginningDatetime, 'day')
          )
            return {}

          return {
            bookingLimitDatetime: updateBookingLimitDatetime({
              isEvent,
              previousBeginningDatetime: beginningDatetime,
              previousBookingLimitDatetime: bookingLimitDatetime,
              timezone,
            }),
          }
        },
      },
      {
        field: 'beginningDatetime',
        updates: (beginningDatetime, fieldName, { bookingLimitDatetime }) => ({
          bookingLimitDatetime: updateBookingLimitDatetime({
            isEvent,
            previousBeginningDatetime: beginningDatetime,
            previousBookingLimitDatetime: bookingLimitDatetime,
            timezone,
          }),
        }),
      }
    )
)(mapArgsToCacheKey)

export default adaptBookingLimitDatetimeGivenBeginningDatetime
