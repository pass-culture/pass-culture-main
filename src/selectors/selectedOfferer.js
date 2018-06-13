import { createSelector } from 'reselect'

import { NEW } from '../utils/config'

export default createSelector(
  state => get(state, `form.occasionsById`),
  (state, ownProps) => ownProps.match.params.occasionId,
  (occasionsById, occasionId) => occasionsById && occasionId === 'nouveau'
    ? occasionsById[NEW]
    : occasionsById[occasionId]
)
