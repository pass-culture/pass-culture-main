import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  offerers => offerers && offerers.map(o =>
    ({ label: o.name, value: o.id }))
)
