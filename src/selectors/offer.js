import createCachedSelector from 're-reselect'

import offersSelector from './offers'

export default createCachedSelector(
  state => offersSelector(state),
  (state, eventOccurenceId) => eventOccurenceId,
  (offers, eventOccurenceId) => offers.find(offer =>
    offer.eventOccurenceId === eventOccurenceId)
)(
  (state, eventOccurenceId) => eventOccurenceId || ''
)
