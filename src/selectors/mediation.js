import createCachedSelector from 're-reselect'

import mediationsSelector from './mediations'

export default createCachedSelector(
  state => mediationsSelector(state),
  (state, mediationId) => mediationId,
  (mediations, mediationId) => mediations.find(m => m.id === mediationId)
)((state, mediationId) => mediationId || '')
