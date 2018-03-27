import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectMediation from './mediation'
import selectOffer from './offer'

export default createSelector(
  (state, ownProps) => selectMediation(state, ownProps),
  (state, ownProps) => selectOffer(state, ownProps),
  (mediation, offer) => {
    return get(offer, 'eventOccurence.event')
      || get(offer, 'thing')
      || get(mediation, 'event')
      || get(mediation, 'thing')
  }
)
