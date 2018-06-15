import { createSelector } from 'reselect'

import selectProviders from './providers'

export default createSelector(
  state => state.data.providers,
  providers => providers && providers.map(p =>
    ({ label: p.name, value: p.id }))
)
