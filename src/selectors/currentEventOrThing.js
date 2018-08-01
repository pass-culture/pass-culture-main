import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOffer from './currentMediation'
// import selectCurrentOffer from './currentOffer'
// import getSource from '../getters/source'

export default createSelector(
  selectCurrentOffer,
  offer => get(offer, 'eventOrThing')
)
