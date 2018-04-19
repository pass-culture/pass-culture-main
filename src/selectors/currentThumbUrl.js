import { createSelector } from 'reselect'

import selectCurrentMediation from './currentMediation'
import selectCurrentSource from './currentSource'
import selectCurrentOffer from './currentOffer'
import getThumbUrl from '../getters/thumbUrl'

export default createSelector(
  selectCurrentMediation,
  selectCurrentSource,
  selectCurrentOffer,
  getThumbUrl
)
