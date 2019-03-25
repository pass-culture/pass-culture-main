import createCachedSelector from 're-reselect'

import selectMediationsByOfferId from './selectMediationsByOfferId'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

const selectActiveMediationsByOfferId = createCachedSelector(
  selectMediationsByOfferId,
  mediations => mediations.filter(mediation => mediation.isActive)
)(mapArgsToCacheKey)

export default selectActiveMediationsByOfferId
