import get from 'lodash.get'
import { createSelector } from 'reselect'

import createTypesSelector from './createTypes'
import createEventSelector from './createEvent'
import createThingSelector from './createThing'


const eventSelector = createEventSelector()
const thingSelector = createThingSelector()
const typesSelector = createTypesSelector()

export default () => createSelector(
  typesSelector,
  (state, eventId, thingId, formLabel) => eventSelector(state, eventId),
  (state, eventId, thingId, formLabel) => thingSelector(state, thingId),
  (state, eventId, thingId, formLabel) => formLabel,
  (types, event, thing, formLabel) => {
    // get the tag which is actually the type key in event and thing
    let tag = get(event, 'type')
    let type
    if (tag) {
      type = {
        model: 'EventType',
        tag
      }
    } else {
      tag = get(thing, 'type')
      if (tag) {
        type = {
          model: 'ThingType',
          tag
        }
      } else if (formLabel) {
        const [model, tag] = formLabel.split('.')
        type = {
          model,
          tag
        }
      }
    }
    return type && types.find(t =>
      t.model === type.model && t.tag === type.tag)
  }
)
