import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectMediation from './mediation'
import selectOffer from './offer'

export function getSource (mediation, offer) {
  return get(offer, 'eventOccurence.event')
    || get(offer, 'thing')
    || get(mediation, 'event')
    || get(mediation, 'thing')
}

export default createSelector(
  selectMediation,
  selectOffer,
  getSource
)
