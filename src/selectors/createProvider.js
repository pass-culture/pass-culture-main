import { createSelector } from 'reselect'

export default providersSelector => createSelector(
  providersSelector,
  (state, providerId) => providerId,
  (providers, providerId) => providers
    .find(p => p.id === providerId) || {}
)
