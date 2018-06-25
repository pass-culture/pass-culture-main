import get from 'lodash.get'
import { createSelector } from 'reselect'

const createThingSelect = () => createSelector(
  state => get(state, 'data.things'),
  (state, thingId) => thingId,
  (things, thingId) => things.find(thing =>
    thing.id === thingId)
)
export default createThingSelect

