import createCachedSelector from 're-reselect';

import providersSelector from './providers'

export default createCachedSelector(
  (state) => providersSelector(state),
  (state, providerId) => providerId,
  (providers, providerId) => providers
    .find(p => p.id === providerId),
  (state, providerId) => providerId
)
