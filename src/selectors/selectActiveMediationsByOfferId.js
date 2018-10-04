import createCachedSelector from 're-reselect'

import mediationsSelector from './mediations'

function mapArgsToKey(state, offerId) {
  return offerId || ''
}

const selectActiveMediationsByOfferId = createCachedSelector(
  mediationsSelector,
  mediations => mediations.filter(mediation => mediation.isActive)
)(mapArgsToKey)

export default selectActiveMediationsByOfferId
