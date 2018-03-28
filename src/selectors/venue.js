import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectSource from './source'
import selectOffer from './offer'

export default createSelector(
  selectSource,
  selectOffer,
  (offer, source) => {
    console.log('offer, source', offer, source)
    return get(offer, 'eventOccurence.venue') ||
      get(offer, 'venue') ||
      get(source, 'eventOccurence.venue') ||
      get(source, 'venue')
  }
)
