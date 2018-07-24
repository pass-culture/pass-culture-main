import get from 'lodash.get'
import { createSelector } from 'reselect'

export function errorKeyToFrenchKey (errorKey) {
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
  state => get(state, 'errors.occurence'),
  state => get(state, 'errors.offer'),
  (occurenceErrors, offerErrors) => {
    const errors = Object.assign({}, occurenceErrors, offerErrors)
    const e = Object.keys(errors)
          .filter(errorKeyToFrenchKey)
          .reduce((result, errorKey) =>
            Object.assign(
              { [errorKeyToFrenchKey(errorKey)]: errors[errorKey] },
              result
            ), null)
    return e
  }
)
