import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectOffer from './offer'

export default createSelector(
  selectOffer,
  offer => offer && offer.price === 0 && offer.publicPrice && get(offer, 'offerer.name')
)
