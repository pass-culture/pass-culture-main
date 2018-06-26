import get from 'lodash.get'
import { createSelector } from 'reselect'

import createMediationsSelector from './createMediations'

const createSelectMediation = () => createSelector(
  createMediationsSelector(),
  (state, mediationId) => mediationId,
  (mediations, mediationId) => {
    return mediations.filter(m => m.id === mediationId)
  }
)
export default createSelectMediation
