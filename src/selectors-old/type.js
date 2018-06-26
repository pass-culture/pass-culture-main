import get from 'lodash.get'
import { createSelector } from 'reselect'

import createEventSelect from './createEvent'
import createThingSelect from './createThing'
import typesSelect from './types'

const createSelectType = () => createSelector(
  createEventSelect(),
  createThingSelect(),
  typesSelect,
  (event, thing, types) => {
    const tag = get(event, 'type') || get(thing, 'type')
    return types && types.find(type => type.tag === tag)
  }
)
export default createSelectType
