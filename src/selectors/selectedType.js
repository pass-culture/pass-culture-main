import get from 'lodash.get'
import { createSelector } from 'reselect'

import { NEW } from '../utils/config'

export default createSelector(
  state => state.data.types,
  state => get(state, 'form.occasionsById'),
  (state, ownProps) => get(ownProps, 'currentOccasion.id'),
  (types, occasionsById, occasionId) => {
    const typeValue = occasionsById &&
      get(occasionsById, `${occasionId || NEW}.type`)
    return typeValue && types && types.find(type => type.value === typeValue)
  }
)
