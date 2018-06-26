import { createSelector } from 'reselect'

import createProvidersSelector from './createProviders'

export default () => createSelector(
  createProvidersSelector(),
  (state, providerId) => providerId,
  (providers, providerId) => providers
    .find(p => p.id === providerId) || {}
)
