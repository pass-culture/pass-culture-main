import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectProviders from './providers'

import { NEW } from '../utils/config'

export default createSelector(
  selectProviders,
  state => get(state, `form.venueProvidersById.${NEW}`),
  (providers, formVenueProvider) => providers &&
    formVenueProvider &&
    providers.find(p => p.id === formVenueProvider.providerId)
)
