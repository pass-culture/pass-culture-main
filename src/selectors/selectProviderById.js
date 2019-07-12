import createCachedSelector from 're-reselect'

import selectProviders from './selectProviders'

function mapArgsToCacheKey(state, providerId) {
  return providerId || ''
}

const selectProviderById = createCachedSelector(
  state => selectProviders(state),
  (state, providerId) => providerId,
  (providers, providerId) => providers.find(p => p.id === providerId)
)(mapArgsToCacheKey)

export default selectProviderById
