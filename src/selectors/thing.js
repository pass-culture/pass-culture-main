import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.things,
  (state, ownProps) => get(ownProps, 'occasion.thingId'),
  (things, thingId) => things && things.find(thing =>
    thing.id === thingId)
)
