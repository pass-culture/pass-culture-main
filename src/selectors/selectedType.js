import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectFormOccasion from './formOccasion'
import createSelectType from './type'

export default createSelector(
  createSelectType(),
  selectFormOccasion,
  (type, formOccasion) =>
    type || get(formOccasion, 'type')
)
