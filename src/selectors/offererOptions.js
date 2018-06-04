import { createSelector } from 'reselect'

export default createSelector(
  state => state.user && state.user.offerers,
  offerers => offerers && offerers.map(o =>
    ({ label: o.name, value: o.id }))
)
