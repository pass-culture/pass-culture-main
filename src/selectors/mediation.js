import createCachedSelector from 're-reselect';

import createMediationsSelector from './createMediations'

const mediationsSelector = createMediationsSelector()

export default createCachedSelector(
  (state, mediationId) => mediationsSelector(state),
  (state, mediationId) => mediationId,
  (mediations, mediationId) => {
    return mediations.find(m => m.id === mediationId)
  },
  (state, mediationId) => mediationId,
)
