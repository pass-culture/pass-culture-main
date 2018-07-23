import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

import offersSelector from './offers'

export default createCachedSelector(
  state => offersSelector(state),
  (state, eventOccurenceId) => eventOccurenceId,
  (offers, eventOccurenceId) => {
    const offer = offers.find(offer =>
      offer.eventOccurenceId === eventOccurenceId)
    return Object.assign({},
      {
        available: get(offer, 'available'),
        bookingLimitDatetime: moment(get(offer, 'bookingLimitDatetime'))
          .add(1, 'day')
          .toISOString(),
        price: get(offer, 'price'),
      }, offer)
  }
)(
  (state, eventOccurenceId) => eventOccurenceId || ''
)
