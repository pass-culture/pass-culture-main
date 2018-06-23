import get from 'lodash.get'
import { createSelector } from 'reselect'

const createSelectThing = () => createSelector(
  state => state.data.things,
  (state, ownProps) => get(ownProps, 'occasion.thingId'),
  (things, thingId) => things && things.find(thing =>
    thing.id === thingId)
)
export default createSelectThing

export const selectCurrentThing = createSelectThing()
