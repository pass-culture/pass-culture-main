import { createSelector } from 'reselect'


export default createSelector(
  state => state.data.recommendations || [],
  (recommendations) => {
    let recosById = {}
    recommendations.map(r => recosById[r.id] = r)
    return Object.values(recosById)
  }
)
