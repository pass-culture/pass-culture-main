import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentMediation from './currentMediation'
import selectCurrentOffer from './currentOffer'

export default createSelector(
  (state, ownProps) => selectCurrentMediation(state, ownProps),
  (state, ownProps) => selectCurrentOffer(state, ownProps),
  (currentMediation, currentOffer) => {
    return get(currentOffer, 'eventOccurence.event')
      || get(currentOffer, 'thing')
      || get(currentMediation, 'event')
      || get(currentMediation, 'thing')
  }
)
