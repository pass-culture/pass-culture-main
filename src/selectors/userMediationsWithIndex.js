import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.userMediations || [],
  userMediations => userMediations.map((um, index) =>
    Object.assign(um, { index }))
)
