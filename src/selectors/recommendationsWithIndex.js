import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.recommendations || [],
  recommendations =>
    recommendations.map((reco, index) => Object.assign(reco, { index }))
)
