import { createSelector } from 'reselect'

import { API_URL, THUMBS_URL } from '../utils/config'

export default () => createSelector(
  (state, ownProps) => ownProps.thumbPath,
  (state, ownProps) => ownProps.mediations,
  (thumbPath, mediations) => (
    mediations && mediations[0]
      ? `${THUMBS_URL}/mediations/${mediations[0].id}`
      : `${API_URL}${thumbPath}`
  )
)
