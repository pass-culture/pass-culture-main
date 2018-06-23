import get from 'lodash.get'
import { createSelector } from 'reselect'

import { selectCurrentEvent } from './event'
import selectTypes from './types'
import { selectCurrentThing } from './thing'

const createSelectType = (
  selectEvent,
  selectThing
) => createSelector(
  selectEvent,
  selectThing,
  selectTypes,
  (event, thing, types) => {
    const tag = get(event, 'type') || get(thing, 'type')
    return types && types.find(type => type.tag === tag)
  }
)
export default createSelectType

export const selectCurrentType = createSelectType(
  selectCurrentEvent,
  selectCurrentThing
)
