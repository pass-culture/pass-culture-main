import get from 'lodash.get'
import { createSelector } from 'reselect'


export default () => createSelector(
  state => state.data.mediations,
  (state, ownProps) => ownProps.occasionType,
  (state, ownProps) => get(ownProps, 'occasion.id'),
  (mediations, occasionType, occasionId) =>
    mediations && mediations.filter(m =>
      m[`${occasionType}Id`] === occasionId)
)
