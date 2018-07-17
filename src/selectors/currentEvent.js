import { createSelector } from 'reselect'

import selectCurrentMediation from './currentMediation'
import selectCurrentOffer from './currentOffer'
import getSource from '../getters/source'

export default createSelector(
  selectCurrentMediation,
  selectCurrentOffer,
  getSource
)
