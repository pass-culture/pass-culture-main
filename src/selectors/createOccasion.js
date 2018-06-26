import { createSelector } from 'reselect'

export default occasionsSelector => createSelector(
  occasionsSelector,
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    console.log('occasionId', occasionId, occasions)
    return occasions.find(o => o.id === occasionId)
  }
)
