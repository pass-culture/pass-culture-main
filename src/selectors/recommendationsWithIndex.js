import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.recommendations || [],
  recommendations =>
    recommendations.map((um, index) => Object.assign(um, { index }))
)
