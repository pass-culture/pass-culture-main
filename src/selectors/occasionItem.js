import { createSelector } from 'reselect'

import { THUMBS_URL } from '../utils/config'

export default () => createSelector(
  (state, ownProps) => ownProps.id,
  (state, ownProps) => ownProps.occasionType,
  (state, ownProps) => ownProps.mediations,
  (id, occasionType, mediations) => ({
    thumbUrl: mediations && mediations[0]
      ? `${THUMBS_URL}/mediations/${mediations[0].id}`
      : `${THUMBS_URL}/${occasionType}/${id}`
  })
)
