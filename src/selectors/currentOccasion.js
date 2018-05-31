import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.occasions,
  (state, ownProps) => ownProps.occasionId,
  (occasions, occasionId, occasionQuery) => 
    occasions && occasions.find(o => o.id === occasionId)
)
