import get from 'lodash.get'
import { createSelector } from 'reselect'

import { API_URL, THUMBS_URL } from '../utils/config'

export default (
  selectMediations
) => createSelector(
  selectMediations,
  (state, ownProps) => get(ownProps, 'occasion.thumbPath'),
  (mediations, thumbPath) =>
    get(mediations, '0')
      ? `${THUMBS_URL}/mediations/${mediations[0].id}`
      : `${API_URL}${thumbPath}`
)
