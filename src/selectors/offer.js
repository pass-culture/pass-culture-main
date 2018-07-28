import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

import offersSelector from './offers'

export default createCachedSelector(
  state => offersSelector(state),
  (state, eventOccurenceId) => eventOccurenceId,
  (state, eventOccurenceId, offererId) => offererId,
  (offers, eventOccurenceId, offererId) => {
    const offer = offers.find(offer =>
      offer.eventOccurenceId === eventOccurenceId)
    if (offer) {
      return Object.assign(
        {
          bookingLimitDatetime: moment(get(offer, 'bookingLimitDatetime'))
            .add(1, 'day')
            .toISOString(),
          offererId
        }, offer)
    }
    return {
      eventOccurenceId,
      offererId,
    }
  }
)(
  (state, eventOccurenceId) => eventOccurenceId || ''
)
