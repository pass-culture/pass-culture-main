import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentMediation from './currentMediation'
import selectCurrentOffer from './currentOffer'

export default createSelector(
  state => selectCurrentMediation(state),
  state => selectCurrentOffer(state),
  (currentMediation, currentOffer) => {
    return get(currentOffer, 'eventOccurence')
      || get(currentOffer, 'thing')
      || get(currentMediation, 'event')
      || get(currentMediation, 'thing')
  }
)
