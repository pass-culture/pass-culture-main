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

export const selectStockErrorsByStockId = createSelector(
  (state, stockIdOrNew) => get(state, `errors.stock${stockIdOrNew}`),
  stockErrors => {
    const errors = Object.assign({}, stockErrors)
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

export default selectStockErrorsByStockId
