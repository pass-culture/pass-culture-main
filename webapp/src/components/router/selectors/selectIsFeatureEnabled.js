import { createSelector } from 'reselect'
import selectIsFeatureDisabled from './selectIsFeatureDisabled'

const selectIsFeatureEnabled = createSelector(
  selectIsFeatureDisabled,
  isFeatureDisabled => !isFeatureDisabled
)

export default selectIsFeatureEnabled
