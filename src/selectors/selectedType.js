import get from 'lodash.get'
import { createSelector } from 'reselect'

import { NEW } from '../utils/config'

export default createSelector(
  (state, ownProps) => get(ownProps, 'occasion.id'),
  state => get(state, 'form.occasionsById'),
  (occasionId, occasionsById) => occasionsById &&
    get(occasionsById, `${occasionId || NEW}.type`)
)
