import get from 'lodash.get'
import { createSelector } from 'reselect'

import { NEW } from '../utils/config'

export default createSelector(
  state => state.data.providers,
  state => get(state, `form.venueProvidersById.${NEW}`),
  (providers, formVenueProvider) => providers &&
    formVenueProvider &&
    providers.find(p => p.id === formVenueProvider.providerId)
)
