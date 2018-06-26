import get from 'lodash.get'
import { createSelector } from 'reselect'

import createTypesSelector from './createTypes'

const typesSelector = createTypesSelector()

export default (selectEvent, selectThing) => createSelector(
  typesSelector,
  selectEvent,
  selectThing,
  (types, event, thing, typeLabel) => {
    console.log('event, thing', event, thing)
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
      } else if (typeLabel) {
        const [model, tag] = typeLabel.split('.')
        type = {
          model,
          tag
        }
      }
    }
    console.log('TYPE', type, types)
    return type && types.find(t =>
      t.model === type.model && t.tag === type.tag)
  }
)
