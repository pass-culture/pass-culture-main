import get from 'lodash.get'
import { createSelector } from 'reselect'

import createTypesSelector from './createTypes'

const typesSelector = createTypesSelector()

export default (selectEvent, selectThing) => createSelector(
  typesSelector,
  selectEvent,
  selectThing,
  (state, eventOrThingId, formLabel) => formLabel,
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
    console.log('typeqsdqd', type, types)
    return type && types.find(t =>
      t.model === type.model && t.tag === type.tag)
  }
)
