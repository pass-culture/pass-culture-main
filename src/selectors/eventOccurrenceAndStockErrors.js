import get from 'lodash.get'
import { createSelector } from 'reselect'

export function errorKeyToFrenchKey(errorKey) {
  switch (errorKey) {
    case 'available':
      return 'Places'
    case 'beginningDatetime':
      return 'Date de début'
    case 'bookingLimitDatetime':
      return 'Date de réservation'
    case 'endDatetime':
      return 'Date de fin'
    case 'price':
      return 'Prix'
    default:
      return
  }
}

export default createSelector(
  (state, eventOccurrenceIdOrNew, stockIdOrNew) =>
    get(state, `errors.eventOccurrence${eventOccurrenceIdOrNew}`),
  // quick and dirty fix
  // MERGE_ERRORS make "stockJ4" name with eventOccurrence id and not stock id
  // shared/src/components/forms/Form.js

  (state, eventOccurrenceIdOrNew, stockIdOrNew) =>
    get(state, `errors.stock${eventOccurrenceIdOrNew}`),

  (state, eventOccurrenceIdOrNew, stockIdOrNew) =>
    get(state, `errors.stock${stockIdOrNew}`),

  (eventOccurrenceErrors, eventOccurrenceStockErrors, stockErrors) => {
    const errors = Object.assign(
      {},
      eventOccurrenceErrors,
      eventOccurrenceStockErrors,
      stockErrors
    )
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
