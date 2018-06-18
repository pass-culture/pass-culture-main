import { createSelector } from 'reselect'

import selectProviders from './providers'

export default createSelector(
  selectProviders,
  providers => providers && providers.map(p =>
    ({ label: p.name, value: p.id }))
)
