import get from 'lodash.get';
import { createSelector } from 'reselect'

import selectCurrentOffer from './currentOffer'

export default createSelector(
  selectCurrentOffer,
  currentOffer => currentOffer
    && currentOffer.price === 0
    && currentOffer.publicPrice
    && get(currentOffer, 'offerer.name')
)
