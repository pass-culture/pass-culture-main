import createCachedSelector from 're-reselect'

import selectMediationsByOfferId from './selectMediationsByOfferId'

function mapArgsToKey(state, offerId) {
  return offerId || ''
}

const selectActiveMediationsByOfferId = createCachedSelector(
  selectMediationsByOfferId,
  mediations => mediations.filter(mediation => mediation.isActive)
)(mapArgsToKey)

export default selectActiveMediationsByOfferId
