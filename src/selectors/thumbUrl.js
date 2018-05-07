import { createSelector } from 'reselect'

import getThumbUrl from '../getters/thumbUrl'

export default createSelector(
  (state, ownProps) => state,
  getThumbUrl
)
