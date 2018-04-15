import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.userMediations || [],
  userMediations => userMediations.map((um, i) =>
    Object.assign(um, {index: i}))
)
