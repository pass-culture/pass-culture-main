import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectFormOccasion from './formOccasion'

export default createSelector(
  selectFormOccasion,
  (state, ownProps) => get(ownProps, 'currentOccasion.typeOption'),
  (formOccasion, typeOption) =>
    get(formOccasion, 'type') ||
    get(typeOption, 'value')
)
