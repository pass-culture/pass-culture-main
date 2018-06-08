import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.providerTypes,
  providerTypes => providerTypes && providerTypes.map(p =>
    ({ label: p.name, value: p.localClass }))
)
