import { createSelector } from 'reselect'

import createProvidersSelector from './createProviders'

export default (providersSelector=createProvidersSelector()) => createSelector(
  providersSelector,
  (state, providerId) => providerId,
  (providers, providerId) => providers
    .find(p => p.id === providerId)
)
