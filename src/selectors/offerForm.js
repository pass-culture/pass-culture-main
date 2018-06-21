import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedType from './selectedType'

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
  (state, ownProps) => get(ownProps, 'currentOccasion.type'),
  (state, ownProps) => get(ownProps, 'currentOccasion.modelName'),
  (formType, propsType, modelName) => {

    const formTypeValue = get(formType, 'value')

    const isEventType = modelName === 'Event'
      || (propsType || '').split('.')[0] === 'EventType'
      || (formTypeValue || '').split('.')[0] === 'EventType'

    let requiredFields = requiredEventAndThingFields

    if (isEventType) {
      requiredFields = requiredFields.concat(requiredEventFields)
    }

    return {
      isEventType,
      requiredFields
    }
  }
)
