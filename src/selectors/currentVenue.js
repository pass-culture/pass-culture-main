import { createSelector } from 'reselect'

import selectCurrentSource from './currentSource'
import selectCurrentOffer from './currentOffer'
import getVenue from '../getters/venue'


export default createSelector(
  selectCurrentSource,
  selectCurrentOffer,
  getVenue
)
