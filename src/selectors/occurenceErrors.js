import { createSelector } from 'reselect'

export function errorToKey (error) {
  switch (error) {
    case 'available':
      return 'Places'
    case 'price':
      return 'Prix'
    default:
      return
  }
}

export default createSelector(
  state => state.errors,
  errors => {
    const occurenceErrors = {}
    Object.keys(errors).filter(errorToKey).forEach(
      error => {
        occurenceErrors[errorToKey(error)] = errors[error]
      }
    )
    if (Object.keys(occurenceErrors).length) {
      return occurenceErrors
    }
  }
)
