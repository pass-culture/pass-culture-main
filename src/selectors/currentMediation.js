import { createSelector } from 'reselect'

import selectCurrentUserMediation from './currentUserMediation'
import getMediation from '../getters/mediation'

export default createSelector(
  selectCurrentUserMediation,
  getMediation
)
