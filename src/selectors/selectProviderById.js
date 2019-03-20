import createCachedSelector from 're-reselect'

import selectProviders from './selectProviders'

function mapArgsToKey(state, providerId) {
  return providerId || ''
}

export const selectProviderById = createCachedSelector(
  state => selectProviders(state),
  (state, providerId) => providerId,
  (providers, providerId) => providers.find(p => p.id === providerId)
)(mapArgsToKey)

export default selectProviderById
