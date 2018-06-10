import get from 'lodash.get'
import { createSelector } from 'reselect'

import { NEW } from '../utils/config'

export default createSelector(
  state => state.data.providers,
  state => get(state, `form.newVenueProvidersById.${NEW}`),
  (providers, newVenueProvider) => providers && newVenueProvider && providers.find(p =>
    p.id === newVenueProvider.providerId)
)
