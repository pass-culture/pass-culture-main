import { createSelector } from 'reselect'

export default occasionsSelector => createSelector(
  occasionsSelector,
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    if (!occasionId)
      return occasions

    return occasions.find(o => o.id === occasionId)
  }
)
