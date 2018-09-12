import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, stock) => stock,
  (state, stock, offerId) => offerId,
  (state, stock, offerId, eventOccurrenceId) => eventOccurrenceId,
  (state, stock, offerId, eventOccurrenceId, offererId) => offererId,
  (stock, offerId, eventOccurrenceId, offererId) =>
    Object.assign(
      {
        bookingLimitDatetime:
          get(stock, 'bookingLimitDatetime') &&
          moment(get(stock, 'bookingLimitDatetime'))
            .add(1, 'day')
            .toISOString(),
        eventOccurrenceId,
        offerId,
        offererId,
      },
      stock
    )
)(
  (state, stock, offerId, eventOccurrenceId, offererId) =>
    `${offerId || ''}/${eventOccurrenceId || ''}/${offererId || ''}`
)
