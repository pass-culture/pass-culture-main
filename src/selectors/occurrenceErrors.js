import get from 'lodash.get'
import { createSelector } from 'reselect'

export function errorKeyToFrenchKey(errorKey) {
  switch (errorKey) {
    case 'available':
      return 'Places'
    case 'beginningDatetime':
      return 'Date'
    case 'endDatetime':
      return 'Heure de fin'
    case 'price':
      return 'Prix'
    default:
      return
  }
}

export default createSelector(
  state => get(state, 'errors.eventOccurrence'),
  state => get(state, 'errors.offer'),
  (eventOccurrenceErrors, offerErrors) => {
    const errors = Object.assign({}, eventOccurrenceErrors, offerErrors)
    const e = Object.keys(errors)
      .filter(errorKeyToFrenchKey)
      .reduce(
        (result, errorKey) =>
          Object.assign(
            { [errorKeyToFrenchKey(errorKey)]: errors[errorKey] },
            result
          ),
        null
      )
    return e
  }
)
