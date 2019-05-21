import createDecorator from 'final-form-calculate'
import createCachedSelector from 're-reselect'

import updateBookingLimitDatetime from './updateBookingLimitDatetime'

const mapArgsToCacheKey = ({ isEvent, timezone }) =>
  `${isEvent || ''} ${timezone || ''}`

export const adaptBookingLimitDatetimeGivenBeginningDatetime = createCachedSelector(
  ({ isEvent }) => isEvent,
  isEvent =>
    createDecorator(
      {
        field: 'bookingLimitDatetime',
        updates: (bookingLimitDatetime, fieldName, allValues) =>
          updateBookingLimitDatetime({
            isEvent,
            previousBeginningDatetime: allValues.beginningDatetime,
            previousBookingLimitDatetime: bookingLimitDatetime,
          }),
      },
      {
        field: 'beginningDatetime',
        updates: (beginningDatetime, fieldName, allValues) =>
          updateBookingLimitDatetime({
            isEvent,
            previousBeginningDatetime: beginningDatetime,
            previousBookingLimitDatetime: allValues,
          }),
      }
    )
)(mapArgsToCacheKey)

export default adaptBookingLimitDatetimeGivenBeginningDatetime
