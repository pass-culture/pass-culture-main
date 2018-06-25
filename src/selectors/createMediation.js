import get from 'lodash.get'
import { createSelector } from 'reselect'

import createMediationsSelect from './createMediations'
import createOccasionSelect from './createOccasion'

const createSelectMediation = () => createSelector(
  createMediationsSelect(),
  (state, mediationId) => mediationId,
  (mediations, mediationId) => {
    return mediations.filter(m => m.id === mediationId)
  }
)
export default createSelectMediation
