import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentSource from './currentSource'
import selectCurrentOffer from './currentOffer'

export default createSelector(
  state => selectCurrentSource(state),
  state => selectCurrentOffer(state),
  (currentOffer, currentSource) => {
    return get(currentOffer, 'eventOccurence.venue') ||
      get(currentOffer, 'venue') ||
      get(currentSource, 'eventOccurence.venue') ||
      get(currentSource, 'venue')
  }
)
