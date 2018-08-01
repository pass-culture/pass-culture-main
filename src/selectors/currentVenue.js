import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOffer from './currentOffer'
// import getVenue from '../getters/venue'

export default createSelector(
  selectCurrentOffer,
  currentOffer => get(currentOffer, 'venue')
)
