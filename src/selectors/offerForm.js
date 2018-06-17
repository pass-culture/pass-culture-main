import { createSelector } from 'reselect'

import selectSelectedType from './selectedType'

const eventTypes = [
  'ComedyEvent',
  'DanceEvent',
  'Festival',
  'LiteraryEvent',
  'MusicEvent',
  'ScreeningEvent',
  'TheaterEvent'
]

const requiredEventAndThingFields = [
  'name',
  'type',
  'description',
  'contactName',
  'contactEmail',
]

const requiredEventFields = [
  'durationMinutes',
]

export default createSelector(
  selectSelectedType,
  type => {
    const isEventType = type && eventTypes.includes(type)
    const requiredFields = isEventType
      ? requiredEventAndThingFields.concat(requiredEventFields)
      : requiredEventAndThingFields
    return {
      isEventType,
      requiredFields
    }
  }
)
