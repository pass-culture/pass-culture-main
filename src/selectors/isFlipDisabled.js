import { createSelector } from 'reselect'

import selectIsCurrentTuto from './isCurrentTuto'
import selectCurrentMediation from './currentMediation'
import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  selectCurrentUserMediation,
  selectIsCurrentTuto,
  selectCurrentMediation,
  (currentUserMediation, isCurrentTuto, currentMediation) =>
    !currentUserMediation
      || (isCurrentTuto && currentMediation.thumbCount === 1)
)
