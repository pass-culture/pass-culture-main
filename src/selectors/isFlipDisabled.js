import { createSelector } from 'reselect'

import selectIsTuto from './isTuto'
import selectUserMediation from './userMediation'
import selectMediation from './mediation'

export default createSelector(
  selectUserMediation,
  selectIsTuto,
  selectMediation,
  (userMediation, isTuto, mediation) => {
    return !userMediation || (isTuto && mediation.thumbCount === 1)
  }
)
