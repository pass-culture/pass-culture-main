import get from 'lodash.get'
import { createSelector } from 'reselect'

const createThingSelect = () => createSelector(
  state => get(state, 'data.things', []),
  (state, params) => params,
  (things, {id, type}) => things.find(thing =>
    type === 'thing' &&
    thing.id === id
  )
)
export default createThingSelect

