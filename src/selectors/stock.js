import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

import stocksSelector from './stocks'

export default createCachedSelector(
  state => stocksSelector(state),
  (state, eventOccurrenceId) => eventOccurrenceId,
  (state, eventOccurrenceId, offererId) => offererId,
  (stocks, eventOccurrenceId, offererId) => {
    const stock = stocks.find(
      stock => stock.eventOccurrenceId === eventOccurrenceId
    )
    if (stock) {
      return Object.assign(
        {
          bookingLimitDatetime: moment(get(stock, 'bookingLimitDatetime'))
            .add(1, 'day')
            .toISOString(),
          offererId,
        },
        stock
      )
    }
    return {
      eventOccurrenceId,
      offererId,
    }
  }
)((state, eventOccurrenceId) => eventOccurrenceId || '')
