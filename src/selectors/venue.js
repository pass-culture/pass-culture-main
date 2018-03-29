import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectSource from './source'
import selectOffer from './offer'

export function getVenue (source, offer) {
  return get(offer, 'eventOccurence.venue') ||
    get(offer, 'venue') ||
    get(source, 'eventOccurence.venue') ||
    get(source, 'venue')
}

export default createSelector(
  selectSource,
  selectOffer,
  getVenue
)
