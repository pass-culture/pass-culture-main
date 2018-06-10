import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.providers,
  providers => providers && providers.map(p =>
    ({ label: p.name, value: p.id }))
)
